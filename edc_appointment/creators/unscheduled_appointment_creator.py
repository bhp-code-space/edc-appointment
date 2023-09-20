from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from .appointment_creator import AppointmentCreator
from ..constants import CANCELLED_APPT, IN_PROGRESS_APPT
from ..constants import COMPLETE_APPT, INCOMPLETE_APPT, NEW_APPT


class UnscheduledAppointmentError(Exception):
    pass


class UnscheduledAppointmentNotAllowed(Exception):
    pass


class InvalidParentAppointmentStatusError(Exception):
    pass


class InvalidParentAppointmentMissingVisitError(Exception):
    pass


class AppointmentInProgressError(Exception):
    pass


class UnscheduledAppointmentCreator:
    appointment_creator_cls = AppointmentCreator

    def __init__(self, subject_identifier=None,
                 visit_schedule_name=None, schedule_name=None,
                 visit_code=None, facility=None, appt_status=None,
                 timepoint_datetime=None, suggested_datetime=None,
                 check_appointment=True,
                 **kwargs):
        self._parent_appointment = None
        self.appointment = None
        self.check_appointment = check_appointment
        self.subject_identifier = subject_identifier
        self.visit_schedule_name = visit_schedule_name
        self.schedule_name = schedule_name
        self.visit_code = visit_code
        self.facility = facility
        self.visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name)
        self.schedule = self.visit_schedule.schedules.get(schedule_name)
        self.appointment_model_cls = self.schedule.appointment_model_cls
        visit = self.visit_schedule.schedules.get(
            schedule_name).visits.get(visit_code)
        if not visit:
            raise UnscheduledAppointmentError(
                'Invalid visit. Got None using {'
                f'visit_schedule_name=\'{visit_schedule_name}\','
                f'schedule_name=\'{schedule_name}\','
                f'visit_code=\'{visit_code}\'' + '}')
        if visit.allow_unscheduled:
            # force lookup and parent_appointment exceptions
            self.parent_appointment
            # do not allow if any appointments are IN_PROGRESS
            try:
                obj = self.appointment_model_cls.objects.get(
                    subject_identifier=self.subject_identifier,
                    visit_schedule_name=self.visit_schedule_name,
                    schedule_name=self.schedule_name,
                    appt_status=IN_PROGRESS_APPT)
            except MultipleObjectsReturned as e:
                raise UnscheduledAppointmentError(e)
            except ObjectDoesNotExist:
                pass
            else:
                if check_appointment:
                    raise AppointmentInProgressError(
                        f'Not allowed. Appointment {obj.visit_code}.'
                        f'{obj.visit_code_sequence} is in progress.')

            # don't allow if next appointment is already started.
            next_by_timepoint = self.parent_appointment.next_by_timepoint
            if next_by_timepoint:
                if next_by_timepoint.appt_status not in [NEW_APPT, CANCELLED_APPT]:
                    raise UnscheduledAppointmentError(
                        f'Not allowed. Visit {next_by_timepoint.visit_code} has '
                        'already been started.')
            if not suggested_datetime:
                suggested_datetime = self.parent_appointment.appt_datetime

            if not timepoint_datetime:
                timepoint_datetime = self.parent_appointment.timepoint_datetime
            appointment_creator = self.appointment_creator_cls(
                subject_identifier=self.subject_identifier,
                visit_schedule_name=self.visit_schedule_name,
                schedule_name=self.schedule_name, visit=visit,
                suggested_datetime=suggested_datetime,
                timepoint_datetime=timepoint_datetime,
                visit_code_sequence=self.parent_appointment.next_visit_code_sequence,
                facility=self.facility,
                appointment_model=self.appointment_model_cls._meta.label_lower,
                appt_status=appt_status or IN_PROGRESS_APPT)
            self.appointment = appointment_creator.appointment
        else:
            self.check_appointment_in_progress(
                self.check_appointment, visit_code=self.visit_code)

    def check_appointment_in_progress(self, check=True, visit_code=None):
        if check:
            raise UnscheduledAppointmentNotAllowed(
                f'Not allowed. Visit {visit_code} is not configured for '
                'unscheduled appointments.')

    @property
    def parent_appointment(self, check=True):
        if not self._parent_appointment:
            options = dict(
                subject_identifier=self.subject_identifier,
                visit_schedule_name=self.visit_schedule_name,
                schedule_name=self.schedule_name,
                visit_code=self.visit_code,
                visit_code_sequence=0)
            self._parent_appointment = (
                self.appointment_model_cls.objects.get(**options))
            try:
                self._parent_appointment.visit
            except ObjectDoesNotExist:
                raise InvalidParentAppointmentMissingVisitError(
                    f'Unable to create unscheduled appointment. An unscheduled '
                    f'appointment cannot be created if the parent appointment '
                    f'visit form has not been completed. '
                    f'Got appointment \'{self.visit_code}\'.')
            else:
                if self.check_appointment:
                    if self._parent_appointment.appt_status not in [
                            COMPLETE_APPT, INCOMPLETE_APPT]:
                        raise InvalidParentAppointmentStatusError(
                            f'Unable to create unscheduled appointment. An unscheduled '
                            f'appointment cannot be created if the parent appointment '
                            f'is \'new\' or \'in progress\'. Got appointment '
                            f'\'{self.visit_code}\' is '
                            f'{self._parent_appointment.get_appt_status_display().lower()}.')

        return self._parent_appointment
