use crate::{errors::TypeErrors, graph::{Graph, NodeIdx}, typekind::{FnKind, TypeKind}};

/// self_t.edges().iter(|t| t == self_t)
/// typestore.signature() == self_t.signature()
pub trait TypeCheck {
    fn check_edges(&self, node_idx: NodeIdx) -> Result<(), TypeErrors>;
    fn check_store(&self, node: NodeIdx) -> Result<(), TypeErrors>;
}

impl TypeCheck for Graph {
    fn check_edges(&self, node_idx: NodeIdx) -> Result<(), TypeErrors> {
        let node = self.get_node(node_idx).unwrap();
        let curr_type = node.self_t();
        let curr_edges = node.edges();

        for e in curr_edges {
            let edge = self.get_node(*e).unwrap();
            if edge.self_t() != curr_type {
                return Err(TypeErrors::ConflictingInferredTypes(curr_type.clone(), edge.self_t().clone()));
            }
        }
        Ok(())
    }

    fn check_store(&self, node: NodeIdx) -> Result<(), TypeErrors> {
        let store_sig = self.get_store_signature(node);
        match store_sig {
            Some(sig) => {
                let node_sig = self.signature(node).unwrap();

                if *sig == node_sig {
                    Ok(())
                } else {
                    Err(TypeErrors::ConflictingSignatures(sig.clone(), node_sig.clone()))
                }
            }
            // nothing to check against; OK!
            None => {
                match self.get_node(node).unwrap().self_t() {
                    TypeKind::InBuilt(ib) => {
                        match ib {
                            FnKind::Stub => Ok(()),
                            FnKind::Eq => {
                                let args = self.get_node(node).unwrap().arguments();

                                let first_t = self.get_node(args[0]).unwrap().self_t();
                                // check if all args types are the same
                                for i in 1..args.len() {
                                    if first_t != self.get_node(args[i]).unwrap().self_t() {
                                        return Err(TypeErrors::ConflictingInferredTypes(
                                            first_t.clone(), 
                                            self.get_node(args[i]).unwrap().self_t().clone())
                                        );
                                    }
                                }
                                return Ok(());
                            },
                            // All arguments must be of the type Number
                            FnKind::Add => {
                                let args = self.get_node(node).unwrap().arguments();

                                for arg in args {
                                    if self.get_node(*arg).unwrap().self_t() != TypeKind::Number {
                                        return Err(TypeErrors::ConflictingInferredTypes(
                                            TypeKind::Number, 
                                            self.get_node(*arg).unwrap().self_t().clone())
                                        );
                                    }
                                }
                                return Ok(());
                            }
                            _ => unimplemented!()
                        }
                    }
                    _ => Ok(()),
                }
            }
        }

    }
}

// if a node edges with another node of a stricter type, then the node should narrow itself
// while checking for type compatibility 
pub trait Narrow {
    fn narrow(&mut self, node_idx: NodeIdx) -> Result<NarrowingStatus, TypeErrors>;
}

pub enum NarrowingStatus {
    Narrowed,
    Unchanged,
}

impl Narrow for Graph {

    fn narrow(&mut self, node_idx: NodeIdx) -> Result<NarrowingStatus, TypeErrors> {
        let node = self.get_node(node_idx).unwrap();

        let can_narrow = matches!(node.self_t(), TypeKind::Any | TypeKind::Unknown);

        if !can_narrow {
            return Ok(NarrowingStatus::Unchanged);
        }

        let edges = node.edges();

        let mut curr_t = node.self_t();
        for node in edges {
            let edge_t = self.get_node(*node).unwrap().self_t();
            if edge_t <= curr_t {
                curr_t = edge_t;
            } else {
                return Err(TypeErrors::ConflictingInferredTypes(curr_t, edge_t));
            }
        }

        self.get_node_mut(node_idx).unwrap().set_self_t(curr_t);

        Ok(NarrowingStatus::Narrowed)
    }

}
