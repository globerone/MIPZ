import ast
import os

class ClassInfo:
    def __init__(self, name):
        self.name = name
        self.parent = None
        self.children = set()
        self.methods = set()
        self.private_methods = set()
        self.attributes = set()
        self.private_attributes = set()
        self.metrics = {
        'DIT': 0,
        'NOC': 0,
        'MIF': 0,
        'MHF': 0,
        'AHF': 0,
        'AIF': 0,
        'POF': 0,
    }

class MetricCalculator(ast.NodeVisitor):
    def __init__(self):
        self.classes = {}
        self.current_class = None

    def visit_ClassDef(self, node):
        class_name = node.name
        if class_name not in self.classes:
            self.classes[class_name] = ClassInfo(class_name)
        
        previous_class = self.current_class
        self.current_class = class_name

        for base in node.bases:
            if isinstance(base, ast.Name):
                base_name = base.id
                self.classes[class_name].parent = base_name
                if base_name not in self.classes:
                    self.classes[base_name] = ClassInfo(base_name)
                self.classes[base_name].children.add(class_name)

        self.generic_visit(node)
        self.current_class = previous_class

    def visit_FunctionDef(self, node):
        if self.current_class:
            method_name = node.name
            if method_name.startswith("__") and not method_name.endswith("__"):
                self.classes[self.current_class].private_methods.add(method_name)
            self.classes[self.current_class].methods.add(method_name)
        self.generic_visit(node)

    def visit_Assign(self, node):
        if self.current_class:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    attr_name = target.id
                    if attr_name.startswith("__") and not attr_name.endswith("__"):
                        self.classes[self.current_class].private_attributes.add(attr_name)
                    self.classes[self.current_class].attributes.add(attr_name)
                elif isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                    attr_name = target.attr
                    if attr_name.startswith("__") and not attr_name.endswith("__"):
                        self.classes[self.current_class].private_attributes.add(attr_name)
                    self.classes[self.current_class].attributes.add(attr_name)
        self.generic_visit(node)

    def calculate_dit(self, class_name):
        depth = 0
        current = class_name
        while self.classes[current].parent:
            depth += 1
            current = self.classes[current].parent
        return depth

    def calculate_noc(self, class_name):
        return len(self.classes[class_name].children)

    def calculate_mood_metrics(self):
        for cls in self.classes.values():
            inherited_methods = set()
            inherited_attributes = set()
            current = cls.name

            while self.classes[current].parent:
                parent = self.classes[current].parent
                inherited_methods.update(self.classes[parent].methods)
                inherited_attributes.update(self.classes[parent].attributes)
                current = parent

            if len(inherited_methods) > 0:
                cls.metrics['MIF'] = len(inherited_methods - cls.methods) / len(inherited_methods)
            if len(cls.methods) > 0:
                cls.metrics['MHF'] = len(cls.private_methods) / len(cls.methods)
            if len(cls.attributes) > 0:
                cls.metrics['AHF'] = len(cls.private_attributes) / len(cls.attributes)
            if len(inherited_attributes) > 0:
                cls.metrics['AIF'] = len(inherited_attributes - cls.attributes) / len(inherited_attributes)
            if (len(self.classes) > 0) and (len(cls.methods - inherited_methods) > 0):
                cls.metrics['POF'] = len(inherited_methods) / (len(cls.methods - inherited_methods) * len(self.classes))
            cls.metrics = {key: round(value, 2) for key, value in cls.metrics.items()}
def analyze_source_code(source_code):
    tree = ast.parse(source_code)
    calculator = MetricCalculator()
    calculator.visit(tree)

    for cls in calculator.classes.values():
        cls.metrics['DIT'] = calculator.calculate_dit(cls.name)
        cls.metrics['NOC'] = calculator.calculate_noc(cls.name)

    calculator.calculate_mood_metrics()
    return calculator

def analyze_directory(directory_path):
    metrics = {}
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                    metrics[file_path] = analyze_source_code(source_code)
    return metrics


directory_path = './lib'
metrics_file = analyze_directory(directory_path)
for file, file_metrics in metrics_file.items():
    print(f"Metrics for {file}:")
    MOOD_lib = {'MIF': 0, 'MHF': 0, 'AHF': 0, 'AIF': 0, 'POF': 0}
    for cls in file_metrics.classes.values():
        MOOD_lib['MIF'] += cls.metrics['MIF']
        MOOD_lib['MHF'] += cls.metrics['MHF']
        MOOD_lib['AHF'] += cls.metrics['AHF']
        MOOD_lib['AIF'] += cls.metrics['AIF']
        MOOD_lib['POF'] += cls.metrics['POF']
        print(f"  {cls.name}: {cls.metrics}")

    MOOD_lib = {key: round(value / len (file_metrics.classes), 2) for key, value in MOOD_lib.items()}
    print(f"  MOOD for lib: {MOOD_lib}")
