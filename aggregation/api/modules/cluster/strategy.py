import decimal

from aggregation import db
from aggregation.api.modules.cluster.models import ClusterDeployStrategy, StrategyProductConfig, \
    ClusterInspectInfo, StrategyExpression

from aggregation.api.modules.utils.tasks import send_email


class ExpressionOperationMapping(object):

    def __init__(self, op1, op, op2):
        if isinstance(op1, decimal.Decimal):
            op1 = float(op1)
        if isinstance(op2, decimal.Decimal):
            op2 = float(op2)
        self.op1 = op1
        self.op = op
        self.op2 = op2

    __symbol_method_mapping__ = (
        ("<", "less_than"),
        ("<=", "less_than_or_equal_to"),
        ("=", "equal_to"),
        (">", "more_than"),
        (">=", "more_than_or_equal_to"),
        ("+", "plus"),
        ("-", "less"),
        ("*", "multiply"),
        ("/", "division"),
    )

    def get_value(self):
        method_name = dict(self.__symbol_method_mapping__).get(self.op)
        method = getattr(self, method_name)
        return method()

    def less_than(self):
        return self.op1 < self.op2

    def less_than_or_equal_to(self):
        return self.op1 <= self.op2

    def equal_to(self):
        return self.op1 == self.op2

    def more_than(self):
        return self.op1 > self.op2

    def more_than_or_equal_to(self):
        return self.op1 >= self.op2

    def plus(self):
        return self.op1 + self.op2

    def less(self):
        return self.op1 - self.op2

    def multiply(self):
        return self.op1 * self.op2

    def division(self):
        return self.op1 / self.op2


class Stack(object):
    """模拟栈"""

    def __init__(self, items=None):
        self.items = [] if not items else items

    def is_empty(self):
        return len(self.items) == 0

    def not_empty(self):
        return len(self.items) != 0

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        if not self.is_empty():
            return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)


class DeployClusterChoices(object):

    def __init__(self, product_name: str, region: str):
        self.package_name = product_name
        self.region = region
        self.strategy = self.get_strategy(product_name)

    @classmethod
    def get_strategy(cls, product_name) -> ClusterDeployStrategy:
        strategy = StrategyProductConfig.get_strategy(product_name)
        return strategy

    # def get_current_region_clusters(self) -> List[Cluster]:
    #     query = Cluster.query.filter(Cluster.is_active)
    #     if self.region:
    #         query = query.filter(Cluster.region == self.region)
    #     return query.all()

    def update_cluster_status(self):
        pass


class StrategyUtil(object):

    def __init__(self, cluster_inspect_info: ClusterInspectInfo):
        self.cluster_inspect_info = cluster_inspect_info
        self.cluster = cluster_inspect_info.cluster  # type Cluster

    @classmethod
    def get_strategy(cls):
        return ClusterDeployStrategy.query.filter(ClusterDeployStrategy.is_default).first()

    @classmethod
    def is_express_success(cls, express: StrategyExpression, cluster_inspect_info: ClusterInspectInfo):
        infix = express.infix
        try:
            op1 = ExpressFix(express_str=infix, express_type="infix",
                             query_dict=cluster_inspect_info.query_dict).get_post_fix_value()
        except TypeError as e:
            return False
        except ZeroDivisionError as e:
            return False
        except decimal.InvalidOperation as e:
            return False
        return ExpressionOperationMapping(op1=op1, op=express.relation_operator, op2=express.operator_value).get_value()

    def is_strategy_success(self, strategy: ClusterDeployStrategy) -> bool:
        for expression in strategy.expressions:
            if not self.is_express_success(expression, self.cluster_inspect_info):
                return False
        return True

    def apply_strategy(self):
        strategy = self.get_strategy()
        if not self.is_strategy_success(strategy):
            # need check
            strategy_str = strategy.get_format_str()
            cluster_info = self.dump_cluster_inspect_info()
            content = strategy_str + "\n" + cluster_info
            send_email(["ismewen@163.com"], sub="需要检查集群信息", content=content)
            self.cluster.make_full()
            db.session.add(self.cluster)
            db.session.commit()
        else:
            # normal
            pass

    def dump_cluster_inspect_info(self):
        from .shcemas import ClusterInspectInfoDumpSchema
        s = ClusterInspectInfoDumpSchema()
        data, error = s.dumps(self.cluster_inspect_info)
        return data


class ExpressFix(object):
    express_type = "infix"
    __express_type_choices__ = "infix", "postfix", "preinfix"
    __operation_operator_choices__ = ["+", "-", "*", "/"]
    stack = Stack()
    output_list = []

    priority = {
        "*": 3,
        "/": 3,
        "+": 2,
        "-": 2,
        "(": 2
    }

    def __init__(self, express_str, query_dict, express_type="infix"):
        """
        :param express_str: abc + b + c
        :param express_type:
        """
        self.express_str_list = express_str.split(" ")
        self.set_express_type(express_type)
        self.query_dict = query_dict

    def _init_convert(self):
        self.stack = Stack()
        self.output_list = []

    def set_express_type(self, express_type):
        if express_type not in self.__express_type_choices__:
            raise NameError
        self.express_type = "infix"

    def infix_to_postfix(self):
        self._init_convert()
        for token in self.express_str_list:
            if token == '(':
                self.stack.push(token)
            elif token == ')':
                top_token = self.stack.pop()
                while top_token != '(':
                    self.output_list.append(top_token)
                    top_token = self.stack.pop()
            elif self.is_operation_operator(token):
                # 操作符
                while self.stack.not_empty() and self.priority.get(self.stack.peek()) >= self.priority.get(token):
                    self.output_list.append(self.stack.pop())
                self.stack.push(token)
            else:
                # 变量
                self.output_list.append(token)
        while self.stack.not_empty():
            self.output_list.append(self.stack.pop())
        return self.output_list

    def is_operation_operator(self, token):
        return token in self.__operation_operator_choices__

    def get_post_fix_value(self):
        post_fix = self.infix_to_postfix()
        stack = Stack()
        for token in post_fix:
            if self.is_operation_operator(token):
                op2 = stack.pop()
                op1 = stack.pop()
                res = self.do_math(op1, token, op2)
                stack.push(res)
            else:
                stack.push(self.get_token_value(token))
        return stack.pop()

    def get_token_value(self, token):
        try:
            res = self.query_dict[token]
        except KeyError:
            res = float(token)
        except ValueError:
            raise ValueError
        return res

    def convert_infix(self):
        pass

    def convert_preinfix(self):
        pass

    def convert_postfix(self):
        pass

    def do_math(self, op1, op, op2):
        return ExpressionOperationMapping(op1, op, op2).get_value()
