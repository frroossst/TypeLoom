use crate::typekind::{FnKind, TypeKind};
use crate::typekind::TypeKind::*;


#[derive(Debug, Clone)]
pub struct Signature {
    pub arguments: Vec<TypeKind>,
    pub return_t: TypeKind,
}

impl PartialEq for Signature {

    fn eq(&self, other: &Self) -> bool {
        if self.arguments.iter().zip(other.arguments.iter()).all(|(a, b)| a == b) {
            // check if the return type is equal
            if self.return_t == other.return_t {
                return true;
            }
        }
        false
    }
}

impl PartialEq for TypeKind {
    
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (_, Any) => true,
            (Any, _) => true,
            (_, Unknown) => true,
            (Unknown, _) => true,

            (Function, Function) => true,
            (Number, Number) => true,
            (TypeKind::String, TypeKind::String) => true,
            (Boolean, Boolean) => true,
            (Void, Void) => true,

            // might need a separate weaker and stricter equality check (ref: == vs ===)
            (InBuilt(_a), InBuilt(_b)) => true, // a == b,

            // logic for FnKind return types
            (InBuilt(FnKind::Add), Number) => true,
            (Number, InBuilt(FnKind::Add)) => true,

            // logic for FnKind return types end
            (Object(a), Object(b)) => {
                a.iter().zip(b.iter()).all(|(a, b)| a == b)
            }
            _ => false,
        }
    }
}

impl PartialOrd for TypeKind {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        match (self, other) {
            (_, Any) => Some(std::cmp::Ordering::Less),
            (Any, _) => Some(std::cmp::Ordering::Greater),
            (_, Unknown) => Some(std::cmp::Ordering::Equal),
            (Unknown, _) => Some(std::cmp::Ordering::Equal),
            (Function, Function) => Some(std::cmp::Ordering::Equal),
            (Number, Number) => Some(std::cmp::Ordering::Equal),
            (String, String) => Some(std::cmp::Ordering::Equal),
            (Boolean, Boolean) => Some(std::cmp::Ordering::Equal),
            (Void, Void) => Some(std::cmp::Ordering::Equal),
            // might need a separate weaker and stricter equality check (ref: == vs ===)
            (InBuilt(_a), InBuilt(_b)) => Some(std::cmp::Ordering::Equal), // a == b,
            (Object(a), Object(b)) => {
                if a.len() == b.len() {
                    // check if all key-val tuple pairs are equal
                    // convert typles into hashmaps
                    let a_map: std::collections::HashMap<std::string::String, TypeKind> = a.iter().cloned().collect();
                    let b_map: std::collections::HashMap<std::string::String, TypeKind> = b.iter().cloned().collect();

                    if a_map == b_map {
                        return Some(std::cmp::Ordering::Equal);
                    } else {
                        return None;
                    }
                } else if a.len() < b.len() {
                    let a_map: std::collections::HashMap<std::string::String, TypeKind> = a.iter().cloned().collect();
                    let b_map: std::collections::HashMap<std::string::String, TypeKind> = b.iter().cloned().collect();

                    if a_map.iter().all(|(k, v)| b_map.contains_key(k) && b_map.get(k) == Some(v)) {
                        return Some(std::cmp::Ordering::Less);
                    } else {
                        return None;
                    }
                } else {
                    None
                }
            }
            _ => Some(std::cmp::Ordering::Greater),
        }
    }
}
