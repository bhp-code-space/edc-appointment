# edc-appointment ![Build Status](https://github.com/bhp-code-space/edc-appointment/actions/workflows/django.yml/badge.svg) [![Coverage Status](https://codecov.io/gh/bhp-code-space/edc-appointment/branch/develop/graph/badge.svg?token=04d2458b-c222-4a84-a481-8010e8377b9b)](https://codecov.io/gh/bhp-code-space/edc-data-manager)

This module works closely with `edc_visit_tracking` and `edc_visit_schedule`.

Subject data is collected on predefined timepoints. We describe these data collection timepoints in a `visit_schedule` as provided by `edc-visit-schedule`. In `edc-appointment` timepoints are represented by appointments. `edc-appointment` provides classes for creating and managing appointments.

See also `edc-visit-schedule`. 

### `AppointmentModelMixin`

A model mixin for the Appointment model. Each project may have one appointment model. For example:

    class Appointment(AppointmentModelMixin, RequiresConsentModelMixin, BaseUuidModel):
    
        class Meta(AppointmentModelMixin.Meta):
            consent_model = 'edc_example.subjectconsent'
            app_label = 'edc_example'


### Appointment is a required foreignkey for the visit report

The `Appointment` model is a required foreignkey for the visit report. Be sure to set `on_delete=PROTECT`.

    class SubjectVisit(VisitModelMixin, OffstudyMixin, CreatesMetadataModelMixin, RequiresConsentModelMixin, BaseUuidModel):
    
        appointment = models.OneToOneField(Appointment, on_delete=PROTECT)
    
        objects = VisitModelManager()
    
        class Meta(VisitModelMixin.Meta):
            consent_model = 'edc_example.subjectconsent'
            app_label = 'edc_example'

### `CreatesAppointmentsModelMixin`

A model mixin for the model that triggers the creation of appointments when the model is saved. This is typically an enrollment model.

Adds the model field `facility`. The value of field `facility` tells the `CreateAppointmentsMixin` to create appointments for the subject on dates that are available at the `facility`.

    class Enrollment(EnrollmentModelMixin, CreateAppointmentsMixin, RequiresConsentModelMixin, BaseUuidModel):
    
        class Meta(EnrollmentModelMixin.Meta):
            visit_schedule_name = 'subject_visit_schedule.schedule1'
            consent_model = 'edc_example.subjectconsent'
            app_label = 'edc_example'

When `Enrollment` declared above is saved, one appointment will be created for the subject for each `visit` in schedule `schedule1` of visit_schedule `subject_visit_schedule`. 

Note: the value for `facility` must be provided by the user, either through the form interface or programmatically. 

### Customizing appointment scheduling by `Facility`

see `edc_facility`

### Available Appointment Model Manager Methods

The `Appointment` model is declared with `AppointmentManager`. It has several useful methods. 

#### `first_appointment()`, `last_appointment()`

Returns the first (or last) appointment. If just the `subject_identifier` is provided, the first appointment of the protocol for the subject is returned. To be more specific, provide `{subject_identifier=subject_identifier, visit_schedule_name=visit_schedule_name}`.
To be even more specific,  `{subject_identifier=subject_identifier, visit_schedule_name=visit_schedule_name, schedule_name=schedule_name}`.

The most common usage is to just provide these values with an appointment instance:

    first_appointment = Appointment.objects.first_appointment(appointment=appointment)

#### `next_appointment()`, `previous_appointment()`

The next and previous appointment are relative to the schedule and a visit_code within that schedule. If next is called on the last appointment in the sequence `None` is returned. If previous is called on the first appointment in the sequence `None` is returned.

For example, in a sequence of appointment 1000, 2000, 3000, 4000:

    >>> appointment.visit_code
    1000
    >>> next_appointment = Appointment.objects.next_appointment(appointment=appointment)
    >>> next_appointment.visit_code
    2000

But you can also pass an appointment instance and pass the visit code:

    >>> appointment.visit_code
    1000
    >>> next_appointment = Appointment.objects.next_appointment(appointment=appointment, visit_code=3000)
    >>> next_appointment.visit_code
    4000
If you ask for the next appointment from the last, `None` is returned:

    >>> appointment.visit_code
    4000
    >>> next_appointment = Appointment.objects.next_appointment(appointment=appointment, visit_code=3000)
    >>> next_appointment.visit_code
    AttributeError: 'NoneType' object has no attribute 'visit_code'

The `previous_appointment` acts as expected:

    >>> appointment.visit_code
    1000
    >>> previous_appointment = Appointment.objects.previous_appointment(appointment=appointment)
    >>> previous_appointment.visit_code
    AttributeError: 'NoneType' object has no attribute 'visit_code'

#### `delete_for_subject_after_date()`

This method will delete all appointments for a subject after a given datetime. See also `edc-offstudy`.

`Appointment` is usually a foreignkey of a visit model. It's important when using this method to ensure that when declaring `Appointment` as a foreignkey you explicitly set `on_delete=PROTECT`. If you don't, the deletion will cascade to other related instances -- and that's bad. 

    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)


