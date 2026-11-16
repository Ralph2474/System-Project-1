import json
from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from accounts.decorators import role_login_required
from accounts.models import CustomUser
from applications.models import ApplicationRecord, PlacementRecord
from documents.models import SubmittedDocument
from evaluations.models import EvaluationRecord
from internships.models import InternshipPosting
from timelog.models import DailyTimeLog


@role_login_required(CustomUser.ROLE_STUDENT, CustomUser.ROLE_COORDINATOR, CustomUser.ROLE_COMPANY_SUPERVISOR)
def role_dashboard(request):
    role = request.user.role
    chart_data = {}
    supervisor_students = []

    if role == CustomUser.ROLE_STUDENT:
        placement = PlacementRecord.objects.filter(student=request.user).select_related('internship').first()
        hours_logged = DailyTimeLog.objects.filter(student=request.user).aggregate(total=Sum('hours_completed'))['total'] or Decimal('0')
        required_hours = placement.internship.required_hours if placement and placement.internship else 0
        hours_completed_pct = int((hours_logged / required_hours) * 100) if required_hours else 0
        pending_applications = ApplicationRecord.objects.filter(student=request.user, status=ApplicationRecord.STATUS_PENDING).count()
        documents_submitted = SubmittedDocument.objects.filter(student=request.user).count()
        
        # Student chart data
        # Hours progress over time (last 7 entries)
        recent_logs = DailyTimeLog.objects.filter(student=request.user).order_by('-entry_date')[:7]
        hours_chart = {
            'labels': json.dumps([log.entry_date.strftime('%m/%d') for log in reversed(recent_logs)]),
            'data': json.dumps([float(log.hours_completed) for log in reversed(recent_logs)]),
        }
        
        # Application status breakdown
        app_status_chart = {
            'labels': json.dumps(['Pending', 'Approved', 'Rejected']),
            'data': json.dumps([
                ApplicationRecord.objects.filter(student=request.user, status=ApplicationRecord.STATUS_PENDING).count(),
                ApplicationRecord.objects.filter(student=request.user, status=ApplicationRecord.STATUS_APPROVED).count(),
                ApplicationRecord.objects.filter(student=request.user, status=ApplicationRecord.STATUS_REJECTED).count(),
            ])
        }
        
        chart_data = {
            'hours_chart': hours_chart,
            'app_status_chart': app_status_chart,
        }
        
        activity_items = [
            {'label': 'Hours logged', 'value': f'{hours_logged} of {required_hours} target'},
            {'label': 'Applications', 'value': f'{pending_applications} pending review'},
            {'label': 'Documents', 'value': f'{documents_submitted} submitted'},
        ]
        card_labels = ['Hours completed', 'Pending applications', 'Documents submitted']
        card_values = [f'{hours_completed_pct}%', pending_applications, documents_submitted]
        
    elif role == CustomUser.ROLE_COMPANY_SUPERVISOR:
        placements = PlacementRecord.objects.filter(company_supervisor=request.user).select_related('student', 'internship')
        student_ids = [placement.student_id for placement in placements]
        hours_logged = DailyTimeLog.objects.filter(student_id__in=student_ids).aggregate(total=Sum('hours_completed'))['total'] or Decimal('0')
        required_hours = sum(placement.internship.required_hours for placement in placements)
        hours_completed_pct = int((hours_logged / required_hours) * 100) if required_hours else 0
        pending_applications = ApplicationRecord.objects.filter(status=ApplicationRecord.STATUS_PENDING, internship__in=[placement.internship for placement in placements]).count()
        documents_submitted = SubmittedDocument.objects.filter(student_id__in=student_ids).count()
        
        # Company supervisor chart data
        # Student evaluations ratings
        evaluations = EvaluationRecord.objects.filter(supervisor=request.user)
        evaluated_student_ids = set(evaluations.values_list('student_id', flat=True))
        pending_evaluations = 0
        eval_chart = {
            'labels': json.dumps([f"{ev.student.username}" for ev in evaluations]),
            'data': json.dumps([float(ev.rating) for ev in evaluations]),
        }
        
        # Hours completion by student
        student_hours_chart = {
            'labels': json.dumps([]),
            'completed': json.dumps([]),
            'required': json.dumps([]),
        }
        labels_list = []
        completed_list = []
        required_list = []
        for placement in placements:
            student_completed = DailyTimeLog.objects.filter(student=placement.student).aggregate(total=Sum('hours_completed'))['total'] or Decimal('0')
            required = placement.internship.required_hours
            completion_percent = min(int((student_completed / required) * 100), 100) if required else 0
            is_evaluated = placement.student_id in evaluated_student_ids
            pending_evaluations += not is_evaluated
            supervisor_students.append({
                'student': placement.student,
                'internship': placement.internship,
                'hours_completed': student_completed,
                'required_hours': required,
                'completion_percent': completion_percent,
                'is_evaluated': is_evaluated,
            })
            labels_list.append(placement.student.username)
            completed_list.append(float(student_completed))
            required_list.append(float(required))
        
        student_hours_chart = {
            'labels': json.dumps(labels_list),
            'completed': json.dumps(completed_list),
            'required': json.dumps(required_list),
        }
        
        chart_data = {
            'eval_chart': eval_chart,
            'student_hours_chart': student_hours_chart,
        }
        
        activity_items = [
            {'label': 'Hours logged', 'value': f'{hours_logged} of {required_hours} target'},
            {'label': 'Assigned students', 'value': f'{len(placements)} under supervision'},
            {'label': 'Evaluations', 'value': f'{pending_evaluations} still to submit'},
        ]
        card_labels = ['Hours completed', 'Assigned students', 'Evaluations pending']
        card_values = [f'{hours_completed_pct}%', len(placements), pending_evaluations]
        
    else:  # Coordinator
        placements = PlacementRecord.objects.select_related('student', 'internship')
        hours_logged = DailyTimeLog.objects.aggregate(total=Sum('hours_completed'))['total'] or Decimal('0')
        required_hours = sum(placement.internship.required_hours for placement in placements)
        hours_completed_pct = int((hours_logged / required_hours) * 100) if required_hours else 0
        pending_applications = ApplicationRecord.objects.filter(status=ApplicationRecord.STATUS_PENDING).count()
        documents_submitted = SubmittedDocument.objects.filter(status=SubmittedDocument.STATUS_PENDING).count()
        
        # Coordinator chart data
        # Overall statistics
        total_students = CustomUser.objects.filter(role=CustomUser.ROLE_STUDENT).count()
        total_postings = InternshipPosting.objects.count()
        total_placements = PlacementRecord.objects.count()
        
        stats_chart = {
            'labels': json.dumps(['Students', 'Postings', 'Placements', 'Pending Apps']),
            'data': json.dumps([total_students, total_postings, total_placements, pending_applications]),
        }
        
        # Application status breakdown
        app_status_chart = {
            'labels': json.dumps(['Pending', 'Approved', 'Rejected']),
            'data': json.dumps([
                ApplicationRecord.objects.filter(status=ApplicationRecord.STATUS_PENDING).count(),
                ApplicationRecord.objects.filter(status=ApplicationRecord.STATUS_APPROVED).count(),
                ApplicationRecord.objects.filter(status=ApplicationRecord.STATUS_REJECTED).count(),
            ])
        }
        
        # Document status breakdown
        doc_status_chart = {
            'labels': json.dumps(['Pending', 'Validated', 'Rejected']),
            'data': json.dumps([
                SubmittedDocument.objects.filter(status=SubmittedDocument.STATUS_PENDING).count(),
                SubmittedDocument.objects.filter(status=SubmittedDocument.STATUS_VALIDATED).count(),
                SubmittedDocument.objects.filter(status=SubmittedDocument.STATUS_REJECTED).count(),
            ])
        }
        
        chart_data = {
            'stats_chart': stats_chart,
            'app_status_chart': app_status_chart,
            'doc_status_chart': doc_status_chart,
        }
        
        activity_items = [
            {'label': 'Hours logged', 'value': f'{hours_logged} across active placements'},
            {'label': 'Applications', 'value': f'{pending_applications} pending review'},
            {'label': 'Documents', 'value': f'{documents_submitted} awaiting validation'},
        ]
        card_labels = ['Hours completed', 'Pending applications', 'Documents awaiting validation']
        card_values = [f'{hours_completed_pct}%', pending_applications, documents_submitted]

    context = {
        'role': role,
        'role_label': request.user.get_role_display(),
        'card_items': [
            {'label': label, 'value': value}
            for label, value in zip(card_labels, card_values)
        ],
        'progress_width': min(hours_completed_pct, 100),
        'activity_items': activity_items,
        'chart_data': chart_data,
        'supervisor_students': supervisor_students,
    }
    return render(request, 'dashboard/role_dashboard.html', context)
