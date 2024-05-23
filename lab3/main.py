import ast
import os

class ClassInfo:
    def __init__(self, name):
        self.name = name
        self.parent = None
        self.children = set()
        self.methods = set()
        self.attributes = set()
        self.private_attributes = set()

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
            self.classes[self.current_class].methods.add(node.name)
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
        mif = 0
        mhf = 0
        ahf = 0
        aif = 0
        pof = 0

        total_methods = sum(len(cls.methods) for cls in self.classes.values())
        total_attributes = sum(len(cls.attributes) for cls in self.classes.values())
        total_inherited_methods = 0
        total_hidden_methods = 0
        total_inherited_attributes = 0
        total_hidden_attributes = 0
        total_polymorphic_methods = 0

        for cls in self.classes.values():
            inherited_methods = set()
            inherited_attributes = set()
            current = cls.name

            while self.classes[current].parent:
                parent = self.classes[current].parent
                inherited_methods.update(self.classes[parent].methods)
                inherited_attributes.update(self.classes[parent].attributes)
                current = parent

            total_inherited_methods += len(inherited_methods)
            total_hidden_methods += len(inherited_methods & cls.methods) 
            total_polymorphic_methods += len(inherited_methods & cls.methods)

            total_inherited_attributes += len(inherited_attributes - cls.attributes)
            total_hidden_attributes += len(inherited_attributes & cls.attributes)

        if total_methods > 0:
            mif = total_inherited_methods / total_methods
            mhf = total_hidden_methods / total_methods
        if total_attributes > 0:
            ahf = total_hidden_attributes / total_attributes
            aif = total_inherited_attributes / total_attributes
        if len(self.classes) > 0:
            pof = total_polymorphic_methods / len(self.classes)

        return mif, mhf, ahf, aif, pof

def analyze_source_code(source_code):
    tree = ast.parse(source_code)
    calculator = MetricCalculator()
    calculator.visit(tree)

    metrics = {}
    for class_name in calculator.classes:
        metrics[class_name] = {
            'DIT': calculator.calculate_dit(class_name),
            'NOC': calculator.calculate_noc(class_name),
        }

    mif, mhf, ahf, aif, pof = calculator.calculate_mood_metrics()
    metrics['MOOD'] = {
        'MIF': mif,
        'MHF': mhf,
        'AHF': ahf,
        'AIF': aif,
        'POF': pof,
    }

    return metrics

def delete_dict_by_value(main_dict, value_dict):
    keys_to_delete = []
    for key, value in main_dict.items():
        if value == value_dict:
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        del main_dict[key]


def analyze_directory(directory_path):
    metrics = {}
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                    file_metrics = analyze_source_code(source_code)
                    metrics[file_path] = file_metrics
    return metrics


directory_path = './lib'
metrics = analyze_directory(directory_path)
for file, file_metrics in metrics.items():
    print(f"Metrics for {file}:")
    for class_name, class_metrics in file_metrics.items():
        print(f"  {class_name}: {class_metrics}")
