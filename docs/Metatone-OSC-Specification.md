# Metatone OSC Message Specification

## Bonjour Services

- OSC Logging application: `_osclogger._udp.`
- Metatone App: `_metatoneapp._udp.`
- Metatone Classifier Application: `_metatoneclassifier._udp` (unused
  so far...)
- METACLASSIFIER_SERVICE_TYPE `_metatoneclassifier._http._tcp`


## Logging Protocol

    /metatone/online device_id app_id
    /metatone/touch device_id X Y vel
    /metatone/touch/ended device_id
    /metatone/switch device_id switch_id position

## Inter-iPad Messaging

These messages are sent in between Metatone apps on different devices
on the same network.

    /metatone/app device_id message_name message_state

## Classifier Messaging

This message is sent back to Metatone apps to let them know what their
last classified gesture was.

    /metatone/classifier/gesture device_id kind_string

These messages are sent to Metatone apps to let them know the current
state of the ensemble interaction

### Ensemble Events

All `measure_float`s are between 0 and 1.

    /metatone/classifier/ensemble/event/new_idea device_id measure_float
    /metatone/classifier/ensemble/event/solo device_id measure_float
    /metatone/classifier/ensemble/event/parts device_id measure_float
    

### Ensemble States

    /metatone/classifier/ensemble/state "static" spread_float ratio_float
    /metatone/classifier/ensemble/state "diverging" spread_float ratio_float
    /metatone/classifier/ensemble/state "converging" spread_float ratio_float
    /metatone/classifier/ensemble/state "developing" spread_float ratio_float
