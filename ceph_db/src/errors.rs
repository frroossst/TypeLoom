use crate::{type_system::Signature, typekind::TypeKind};

// custom error type 
#[derive(Debug, Clone)]
pub enum TypeErrors {
    ///                     (existing, new)
    ConflictingInferredTypes(TypeKind, TypeKind),
    ///                   (existing, new)
    ConflictingSignatures(Signature, Signature),
    TypeInferenceErrror,
    TypeCheckingError,
}
