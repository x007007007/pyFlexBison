from .generator import GeneratorBase


class TokenRule():
    def __init__(self, token_r, token_name):
        self.token_r = token_r,
        self.token_name = token_name
        self.token_process = None

    def __str__(self):
        ret_list = []
        if self.token_process is not None:
            ret_list.append(f'callback_token_process("{self.token_process.name}");')
        if self.token_name == "":
            ret_list.append(f"return {self.token_name};")
        return f"{self.token_r}     {'{'}  return {self.token_name} {'}'}"

    def bind(self, method):
        self.token_process = method


class FlexGenerator(GeneratorBase):

    def __init__(self):
        self.tokens = []

    def analysis_rule(self):
        for line in self.token_rule.split("\n"):
            rule_string, token_name = line.strip().split("=")
            rule = TokenRule(rule_string.strip(), token_name.strip())
            if rule_method := getattr(self, f't_{token_name.lower()}', None):
                rule.bind(rule_method)
            self.tokens.append(rule)

