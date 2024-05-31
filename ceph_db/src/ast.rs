use crate::typekind::FnKind;

/// A simple AST to parse s-expressions into
/// AST is then used to generate a graph
#[derive(Debug, Clone)]
pub struct AbstractSyntaxTree {
    value: FnKind,
    children: Vec<AbstractSyntaxTree>,
}

impl AbstractSyntaxTree {
    pub fn new(value: FnKind) -> Self {
        AbstractSyntaxTree {
            value,
            children: Vec::new(),
        }
    }

    pub fn get_value(&self) -> &FnKind {
        &self.value
    }

    pub fn set_value(&mut self, value: FnKind) {
        self.value = value;
    }

    pub fn add_child(&mut self, child: AbstractSyntaxTree) {
        self.children.push(child);
    }

    pub fn get_children(&self) -> &Vec<AbstractSyntaxTree> {
        &self.children
    }

    pub fn set_children(&mut self, children: Vec<AbstractSyntaxTree>) {
        self.children = children;
    }

}


