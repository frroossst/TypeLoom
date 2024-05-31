use hashbrown::HashSet;
use indexmap::IndexMap;
use uuid::Uuid;
use crate::bidirectional::{Narrow, TypeCheck};
use crate::errors::TypeErrors;
use crate::{node::Node, type_system::Signature, typekind::TypeKind};
use crate::basal_types;


pub type NodeIdx = usize;

#[derive(Debug)]
pub struct Graph {
    nodes: IndexMap<Uuid, Node>,
    base: Vec<TypeKind>,
    store: IndexMap<NodeIdx, Signature>,
}

impl Graph {
    pub fn new() -> Self {

        let nodes = Graph::get_basal_nodes();
        let mut node_map: IndexMap<Uuid, Node> = IndexMap::new();

        for node in nodes {
            node_map.insert(node.name(), node);
        }

        // add base types
        let base_vec = vec![
            TypeKind::Number,
            TypeKind::String,
            TypeKind::Boolean,
            TypeKind::Void,
            TypeKind::Object(Vec::new()),
            TypeKind::InBuilt(crate::typekind::FnKind::Stub),
            TypeKind::Function,
        ];

        for i in 0..base_vec.len() {
            let node = Node::new(base_vec[i].clone());
            node_map.insert(node.name(), node);
        }

        Graph {
            nodes: node_map,
            base: base_vec,
            store: IndexMap::new(),
        }
    }

    fn get_basal_nodes() -> Vec<Node> {
        let mut nodes = Vec::new();

        basal_types!(nodes);

        nodes
    }

    pub fn len(&self) -> usize {
        self.nodes.len()
    }

    pub fn nodes(&self) -> indexmap::map::Iter<'_, Uuid, Node> {
        self.nodes.iter()
    }

    pub fn add_store_signature(&mut self, idx: NodeIdx, sig: Signature) {
        self.store.insert(idx, sig);
    }

    pub fn get_store_signature(&self, idx: NodeIdx) -> Option<&Signature> {
        self.store.get(&idx)
    }

    pub fn signature(&self, idx: NodeIdx) -> Option<Signature> {
        let node = self.get_node(idx).unwrap();

        let mut arguments: Vec<TypeKind> = Vec::new();

        for args in node.arguments() {
            let arg_node = self.get_node(*args).unwrap().self_t();
            arguments.push(arg_node);
        }

        let return_t = self.get_node(*node.return_t().first().unwrap()).unwrap().self_t();

        Some(Signature {
            arguments,
            return_t,
        })
    }

    /// Two way edge
    pub fn add_edge(&mut self, from: NodeIdx, to: NodeIdx) {
        let from_node = self.get_node_mut(from).unwrap();
        from_node.add_edge(to);
        let to_node = self.get_node_mut(to).unwrap();
        to_node.add_edge(from);

        // trait: Narrow
        self.narrow(from).unwrap();
        self.narrow(to).unwrap();
    }

    pub fn add_node(&mut self, mut node: Node) -> NodeIdx {

        // get the type of the node
        // find the same type in base types of graph
        // add the current node as an edge to base
        // add the base node as an edge to current node
        // return the index of the added node

        let node_type = node.self_t();
        let node_idx = self.nodes.len();

        match node_type {
            // match Any or Unknown
            TypeKind::Any | TypeKind::Unknown => {
                self.nodes.insert(node.name(), node);
                node_idx as NodeIdx
            },
            _ => {
                let base_idx = self.base.iter().position(|t| *t == node_type).unwrap();
                let base_node = self.get_node_mut(base_idx).unwrap();

                base_node.add_edge(node_idx);
                node.add_edge(base_idx);

                self.nodes.insert(node.name(), node);

                // trait: Narrow
                self.narrow(node_idx).unwrap();

                node_idx as NodeIdx
            }
        }
    }

    pub fn get_node_from_uuid(&self, uuid: Uuid) -> Option<&Node> {
        self.nodes.get(&uuid)
    }

    pub fn get_node_mut_from_uuid(&mut self, uuid: Uuid) -> Option<&mut Node> {
        self.nodes.get_mut(&uuid)
    }

    pub fn get_node(&self, idx: NodeIdx) -> Option<&Node> {
        self.nodes.get_index(idx).map(|(_, node)| node)
    }

    pub fn get_node_mut(&mut self, idx: NodeIdx) -> Option<&mut Node> {
        self.nodes.get_index_mut(idx).map(|(_, node)| node)
    }

    pub fn traverse(&self, start: NodeIdx) -> Vec<NodeIdx> {
        let mut visited = HashSet::new();
        let mut result = Vec::new();
        self.dfs(start, &mut visited, &mut result);
        result
    }

    pub fn type_check(&self, start: NodeIdx) -> Result<(), TypeErrors> {
        let mut visited = HashSet::new();
        let mut result = Vec::new();
        self.type_check_dfs(start, &mut visited, &mut result)
    }

    // copy of dfs but with type checking and return Result type
    fn type_check_dfs(&self, node_idx: NodeIdx, visited: &mut HashSet<NodeIdx>, result: &mut Vec<NodeIdx>) -> Result<(), TypeErrors> {
        if visited.contains(&node_idx) {
            return Ok(());
        }
        
        visited.insert(node_idx);
        result.push(node_idx);

        self.check_edges(node_idx)?;
        self.check_store(node_idx)?;

        if let Some(node) = self.get_node(node_idx) {
            for edge in node.edges() {
                self.type_check_dfs(*edge, visited, result)?;
            }
        }

        Ok(())
    }

    fn dfs(&self, node_idx: NodeIdx, visited: &mut HashSet<NodeIdx>, result: &mut Vec<NodeIdx>) {
        if visited.contains(&node_idx) {
            return;
        }
        
        visited.insert(node_idx);
        result.push(node_idx);

        println!("Node: {:#?}", (node_idx));

        if let Some(node) = self.get_node(node_idx) {
            for edge in node.edges() {
                self.dfs(*edge, visited, result);
            }
        }
    }

}
