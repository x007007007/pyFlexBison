from .generator import GeneratorBase


class TokenRule():
    def __init__(self, token_r: str, token_name: str):
        assert isinstance(token_r, str)
        assert isinstance(token_name, str)
        self.token_r = token_r
        self.token_name = token_name
        self.token_process = None

    def __str__(self):
        ret_list = []
        if self.token_process is not None:
            ret_list.append(f'callback_token_process("{self.token_process.__name__}");')
        if self.token_name != "":
            ret_list.append(f"return {self.token_name};")
        return f"{self.token_r}     {'{'}  {'/* */ '.join(ret_list)}  {'}'}"

    def bind(self, method):
        self.token_process = method


class FlexGenerator(GeneratorBase):

    token_rule: str = None

    def __init__(self):
        self.tokens = []
        if self.token_rule is not None:
            self._analysis_rule()

    def _analysis_rule(self):
        for line in self.token_rule.split("\n"):
            if (line := line.strip()) == "": continue
            rule_string, token_name = line.split("=")
            rule_string, token_name = rule_string.strip(), token_name.strip()
            rule = TokenRule(rule_string, token_name)
            if rule_method := getattr(self, f't_{token_name.lower()}', None):
                rule.bind(rule_method)
            self.tokens.append(rule)

    def generate(self) -> str:
        return "\n".join((str(i) for i in self.tokens))
