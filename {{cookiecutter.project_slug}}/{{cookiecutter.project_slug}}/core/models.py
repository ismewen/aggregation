from sqlalchemy.orm.attributes import InstrumentedAttribute

from {cookiecutter.project_slug}} import db
from transitions.extensions import HierarchicalMachine as Machine


class StateMachineModel(db.Model):
    __abstract__ = True

    __states__ = []
    __transitions__ = []
    __state_children_mapping__ = {}

    status = db.Column(db.SmallInteger, index=True, default=0, nullable=False)

    @property
    def state(self):
        return self.status

    @state.setter
    def state(self, value):
        self.status = value

    def __init__(self,*args, **kwargs):
        super(StateMachineModel, self).__init__(*args,**kwargs)

        initial = self._get_initial()

        machine = Machine(model=self,
                          states=self._get_states(),
                          transitions=self.get_transitions(),
                          auto_transitions=False,
                          initial=initial,
                          send_event=True)
        self.fsm = machine

    def get_states(self):
        return self.__states__[:]

    def _get_initial(self):
        if self.status is None:
            self.status = 0
        initial = dict(self.get_states()).get(self.status)
        if initial in self.__state_children_mapping__:
            rel_obj = getattr(self, self.__state_children_mapping__[initial])
            initial = '%s_%s' % (initial, rel_obj.state)
        return initial

    def _get_states(self):
        states_dict = dict(self.get_states())

        for key, value in self.__state_children_mapping__.items():
            child_obj = getattr(self, value)
            state_key = dict((y, x) for (x, y) in self.get_states())[key]
            if child_obj:
                # 当子状态机已存在, 整合子状态机状态
                states_dict[state_key] = {
                    'name': key,
                    'children': child_obj.fsm,
                }
            else:
                # 当子状态机不存在，生成一个空对象，表示初始状态
                child_relation = getattr(self.__class__, value)
                assert isinstance(child_relation, InstrumentedAttribute)
                target_class = child_relation.prop.mapper.class_
                assert issubclass(target_class, StateMachineModel)
                states_dict[state_key] = {
                    'name': key,
                    'children': target_class().fsm,
                }
        print(states_dict)
        states = states_dict.values()
        return list(states)

    @classmethod
    def get_transitions(cls):
        return cls.__transitions__[:]

    def _init_obj_for_state(self, rel):
        if not getattr(self, rel, None):
            class_ = getattr(self.__class__, rel).prop.mapper.class_
            obj = class_()
            db.session.add(obj)
            setattr(self, rel, obj)


class StateMachineClient(StateMachineModel):

    id = db.Column(db.Integer, primary_key=True)

    __states__ = (
        (0, "initial"),
        (1000, "pending"),
        (1001, "active"),
        (1002, "good"),
        (1003, "fraud"),
        (1004, "deleted"),
    )

    __transitions__ = [
        {
            "trigger": "initialize",
            "source": "initial",
            "dest": "pending",
        },
        {
            "trigger": "activate",
            "source": "pending",
            "dest": "active",
        },
        {
            "trigger": "mark_as_good",
            "source": "active",
            "dest": "good",
        },
        {
            "trigger": "mark_as_fraud",
            "source": "active",
            "dest": "fraud",
        },
        {
            "trigger": "delete_state",
            "source": "*",
            "dest": "deleted"
        },
        {
            "trigger": "do_nothing",
            "source": "pending",
            "dest": "pending"
        }
    ]

    __state_children_mapping__ = {
        "good": 'client_ask_for_leave_sub_flow'
    }

    def after_activate(self, *args, **kwargs):
        print("a huge improvement! We have another customer")

    def after_fraud(self, *args, **kwargs):
        print("suspend app!!!")


class ClientAskForLeaveSubFlow(StateMachineModel):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('state_machine_client.id'), unique=True)
    user = db.relationship(StateMachineClient, backref=db.backref("client_ask_for_leave_sub_flow", uselist=False))

    __states__ = (
        (0, "initial"),
        (1001, "processing"),
        (1002, "success"),
        (1003, "failed"),
    )

    __transitions__ = [
        {
            "trigger": "ask_for_leave",
            "source": "initial",
            "dest": "processing",
        },
        {
            "trigger": "approve",
            "source": "processing",
            "dest": "success",
        },
        {
            "trigger": "reject",
            "source": "processing",
            "dest": "failed",
        },
    ]