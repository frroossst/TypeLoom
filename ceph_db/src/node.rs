use uuid::Uuid;
use crate::typekind::TypeKind;
use crate::graph::NodeIdx;


#[derive(Debug, Clone)]
pub struct Node {
    name: Uuid,
    edges: Vec<NodeIdx>,
    self_t: TypeKind,
    arguments: Vec<NodeIdx>,
    return_t: Vec<NodeIdx>,
}

impl Node {
    pub fn new(self_t: TypeKind) -> Node {
        Node {
            name: Uuid::new_v4(),
            edges: Vec::new(),
            self_t,
            arguments: Vec::new(),
            return_t: Vec::new(),
        }
    }

    pub fn name(&self) -> Uuid {
        self.name
    }

    pub fn edges(&self) -> &Vec<NodeIdx> {
        &self.edges
    }

    pub fn self_t(&self) -> TypeKind {
        self.self_t.clone()
    }

    pub fn arguments(&self) -> &Vec<NodeIdx> {
        &self.arguments
    }

    pub fn return_t(&self) -> &Vec<NodeIdx> {
        &self.return_t
    }

    pub fn add_edge(&mut self, idx: NodeIdx) {
        self.edges.push(idx);

    }

    pub fn set_self_t(&mut self, t: TypeKind) {
        self.self_t = t;
    }

    pub fn set_arguments(&mut self, args: Vec<NodeIdx>) {
        self.arguments = args;
    }

    fn set_return_t(&mut self, ret: Vec<NodeIdx>) {
        self.return_t = ret;
    }

    pub fn add_argument(&mut self, arg: NodeIdx) {
        self.arguments.push(arg);
    }

    pub fn add_return_t(&mut self, ret: NodeIdx) {
        self.return_t.push(ret);
    }

    pub fn remove_edge(&mut self, idx: NodeIdx) {
        self.edges.retain(|&x| x != idx);
    }

}
