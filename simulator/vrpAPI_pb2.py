# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vrpAPI.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='vrpAPI.proto',
  package='vrpAPI',
  syntax='proto3',
  serialized_pb=_b('\n\x0cvrpAPI.proto\x12\x06vrpAPI\"!\n\x0bJsonMessage\x12\x12\n\njsonstring\x18\x01 \x01(\t\"\x1e\n\rDoubleMessage\x12\r\n\x05value\x18\x01 \x01(\x01\"#\n\x0fTimeUnitMessage\x12\x10\n\x08timeunit\x18\x01 \x01(\x01\"\x18\n\x0b\x42oolMessage\x12\t\n\x01\x62\x18\x01 \x01(\x08\"\x07\n\x05\x45mpty2\xb2\x06\n\x11SimulatorMessages\x12/\n\x07isReady\x12\r.vrpAPI.Empty\x1a\x13.vrpAPI.BoolMessage\"\x00\x12\x39\n\x11isReadyForOffline\x12\r.vrpAPI.Empty\x1a\x13.vrpAPI.BoolMessage\"\x00\x12\x38\n\x10isReadyForOnline\x12\r.vrpAPI.Empty\x1a\x13.vrpAPI.BoolMessage\"\x00\x12\x30\n\x08loadJson\x12\x13.vrpAPI.JsonMessage\x1a\r.vrpAPI.Empty\"\x00\x12\x37\n\x0floadNewRequests\x12\x13.vrpAPI.JsonMessage\x1a\r.vrpAPI.Empty\"\x00\x12;\n\x0f\x63urrentTimeUnit\x12\x17.vrpAPI.TimeUnitMessage\x1a\r.vrpAPI.Empty\"\x00\x12\x39\n\x0fpauseSimulation\x12\r.vrpAPI.Empty\x1a\x15.vrpAPI.DoubleMessage\"\x00\x12<\n\x12\x63ontinueSimulation\x12\r.vrpAPI.Empty\x1a\x15.vrpAPI.DoubleMessage\"\x00\x12\x30\n\x0etestConnection\x12\r.vrpAPI.Empty\x1a\r.vrpAPI.Empty\"\x00\x12:\n\x12setCurrentSolution\x12\x13.vrpAPI.JsonMessage\x1a\r.vrpAPI.Empty\"\x00\x12*\n\x08shutdown\x12\r.vrpAPI.Empty\x1a\r.vrpAPI.Empty\"\x00\x12\x39\n\x0fstartSimulation\x12\r.vrpAPI.Empty\x1a\x15.vrpAPI.DoubleMessage\"\x00\x12@\n\x16startOfflineSimulation\x12\r.vrpAPI.Empty\x1a\x15.vrpAPI.DoubleMessage\"\x00\x12?\n\x15startOnlineSimulation\x12\r.vrpAPI.Empty\x1a\x15.vrpAPI.DoubleMessage\"\x00\x32\xd3\x02\n\x0eSolverMessages\x12\x35\n\racceptRequest\x12\x13.vrpAPI.JsonMessage\x1a\r.vrpAPI.Empty\"\x00\x12\x32\n\x10notifyEndOffline\x12\r.vrpAPI.Empty\x1a\r.vrpAPI.Empty\"\x00\x12\x31\n\x0fnotifyEndOnline\x12\r.vrpAPI.Empty\x1a\r.vrpAPI.Empty\"\x00\x12\x38\n\x10sendBestSolution\x12\x13.vrpAPI.JsonMessage\x1a\r.vrpAPI.Empty\"\x00\x12\x30\n\x0etestConnection\x12\r.vrpAPI.Empty\x1a\r.vrpAPI.Empty\"\x00\x12\x37\n\x0bgetTimeUnit\x12\r.vrpAPI.Empty\x1a\x17.vrpAPI.TimeUnitMessage\"\x00\x62\x06proto3')
)




_JSONMESSAGE = _descriptor.Descriptor(
  name='JsonMessage',
  full_name='vrpAPI.JsonMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='jsonstring', full_name='vrpAPI.JsonMessage.jsonstring', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=24,
  serialized_end=57,
)


_DOUBLEMESSAGE = _descriptor.Descriptor(
  name='DoubleMessage',
  full_name='vrpAPI.DoubleMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='value', full_name='vrpAPI.DoubleMessage.value', index=0,
      number=1, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=59,
  serialized_end=89,
)


_TIMEUNITMESSAGE = _descriptor.Descriptor(
  name='TimeUnitMessage',
  full_name='vrpAPI.TimeUnitMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='timeunit', full_name='vrpAPI.TimeUnitMessage.timeunit', index=0,
      number=1, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=91,
  serialized_end=126,
)


_BOOLMESSAGE = _descriptor.Descriptor(
  name='BoolMessage',
  full_name='vrpAPI.BoolMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='b', full_name='vrpAPI.BoolMessage.b', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=128,
  serialized_end=152,
)


_EMPTY = _descriptor.Descriptor(
  name='Empty',
  full_name='vrpAPI.Empty',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=154,
  serialized_end=161,
)

DESCRIPTOR.message_types_by_name['JsonMessage'] = _JSONMESSAGE
DESCRIPTOR.message_types_by_name['DoubleMessage'] = _DOUBLEMESSAGE
DESCRIPTOR.message_types_by_name['TimeUnitMessage'] = _TIMEUNITMESSAGE
DESCRIPTOR.message_types_by_name['BoolMessage'] = _BOOLMESSAGE
DESCRIPTOR.message_types_by_name['Empty'] = _EMPTY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

JsonMessage = _reflection.GeneratedProtocolMessageType('JsonMessage', (_message.Message,), dict(
  DESCRIPTOR = _JSONMESSAGE,
  __module__ = 'vrpAPI_pb2'
  # @@protoc_insertion_point(class_scope:vrpAPI.JsonMessage)
  ))
_sym_db.RegisterMessage(JsonMessage)

DoubleMessage = _reflection.GeneratedProtocolMessageType('DoubleMessage', (_message.Message,), dict(
  DESCRIPTOR = _DOUBLEMESSAGE,
  __module__ = 'vrpAPI_pb2'
  # @@protoc_insertion_point(class_scope:vrpAPI.DoubleMessage)
  ))
_sym_db.RegisterMessage(DoubleMessage)

TimeUnitMessage = _reflection.GeneratedProtocolMessageType('TimeUnitMessage', (_message.Message,), dict(
  DESCRIPTOR = _TIMEUNITMESSAGE,
  __module__ = 'vrpAPI_pb2'
  # @@protoc_insertion_point(class_scope:vrpAPI.TimeUnitMessage)
  ))
_sym_db.RegisterMessage(TimeUnitMessage)

BoolMessage = _reflection.GeneratedProtocolMessageType('BoolMessage', (_message.Message,), dict(
  DESCRIPTOR = _BOOLMESSAGE,
  __module__ = 'vrpAPI_pb2'
  # @@protoc_insertion_point(class_scope:vrpAPI.BoolMessage)
  ))
_sym_db.RegisterMessage(BoolMessage)

Empty = _reflection.GeneratedProtocolMessageType('Empty', (_message.Message,), dict(
  DESCRIPTOR = _EMPTY,
  __module__ = 'vrpAPI_pb2'
  # @@protoc_insertion_point(class_scope:vrpAPI.Empty)
  ))
_sym_db.RegisterMessage(Empty)



_SIMULATORMESSAGES = _descriptor.ServiceDescriptor(
  name='SimulatorMessages',
  full_name='vrpAPI.SimulatorMessages',
  file=DESCRIPTOR,
  index=0,
  options=None,
  serialized_start=164,
  serialized_end=982,
  methods=[
  _descriptor.MethodDescriptor(
    name='isReady',
    full_name='vrpAPI.SimulatorMessages.isReady',
    index=0,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_BOOLMESSAGE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='isReadyForOffline',
    full_name='vrpAPI.SimulatorMessages.isReadyForOffline',
    index=1,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_BOOLMESSAGE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='isReadyForOnline',
    full_name='vrpAPI.SimulatorMessages.isReadyForOnline',
    index=2,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_BOOLMESSAGE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='loadJson',
    full_name='vrpAPI.SimulatorMessages.loadJson',
    index=3,
    containing_service=None,
    input_type=_JSONMESSAGE,
    output_type=_EMPTY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='loadNewRequests',
    full_name='vrpAPI.SimulatorMessages.loadNewRequests',
    index=4,
    containing_service=None,
    input_type=_JSONMESSAGE,
    output_type=_EMPTY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='currentTimeUnit',
    full_name='vrpAPI.SimulatorMessages.currentTimeUnit',
    index=5,
    containing_service=None,
    input_type=_TIMEUNITMESSAGE,
    output_type=_EMPTY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='pauseSimulation',
    full_name='vrpAPI.SimulatorMessages.pauseSimulation',
    index=6,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_DOUBLEMESSAGE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='continueSimulation',
    full_name='vrpAPI.SimulatorMessages.continueSimulation',
    index=7,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_DOUBLEMESSAGE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='testConnection',
    full_name='vrpAPI.SimulatorMessages.testConnection',
    index=8,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_EMPTY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='setCurrentSolution',
    full_name='vrpAPI.SimulatorMessages.setCurrentSolution',
    index=9,
    containing_service=None,
    input_type=_JSONMESSAGE,
    output_type=_EMPTY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='shutdown',
    full_name='vrpAPI.SimulatorMessages.shutdown',
    index=10,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_EMPTY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='startSimulation',
    full_name='vrpAPI.SimulatorMessages.startSimulation',
    index=11,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_DOUBLEMESSAGE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='startOfflineSimulation',
    full_name='vrpAPI.SimulatorMessages.startOfflineSimulation',
    index=12,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_DOUBLEMESSAGE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='startOnlineSimulation',
    full_name='vrpAPI.SimulatorMessages.startOnlineSimulation',
    index=13,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_DOUBLEMESSAGE,
    options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_SIMULATORMESSAGES)

DESCRIPTOR.services_by_name['SimulatorMessages'] = _SIMULATORMESSAGES


_SOLVERMESSAGES = _descriptor.ServiceDescriptor(
  name='SolverMessages',
  full_name='vrpAPI.SolverMessages',
  file=DESCRIPTOR,
  index=1,
  options=None,
  serialized_start=985,
  serialized_end=1324,
  methods=[
  _descriptor.MethodDescriptor(
    name='acceptRequest',
    full_name='vrpAPI.SolverMessages.acceptRequest',
    index=0,
    containing_service=None,
    input_type=_JSONMESSAGE,
    output_type=_EMPTY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='notifyEndOffline',
    full_name='vrpAPI.SolverMessages.notifyEndOffline',
    index=1,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_EMPTY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='notifyEndOnline',
    full_name='vrpAPI.SolverMessages.notifyEndOnline',
    index=2,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_EMPTY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='sendBestSolution',
    full_name='vrpAPI.SolverMessages.sendBestSolution',
    index=3,
    containing_service=None,
    input_type=_JSONMESSAGE,
    output_type=_EMPTY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='testConnection',
    full_name='vrpAPI.SolverMessages.testConnection',
    index=4,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_EMPTY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='getTimeUnit',
    full_name='vrpAPI.SolverMessages.getTimeUnit',
    index=5,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_TIMEUNITMESSAGE,
    options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_SOLVERMESSAGES)

DESCRIPTOR.services_by_name['SolverMessages'] = _SOLVERMESSAGES

# @@protoc_insertion_point(module_scope)