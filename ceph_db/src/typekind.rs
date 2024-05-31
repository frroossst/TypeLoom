#[derive(Debug, Clone, Default, Hash)]
pub enum TypeKind {
    #[default]
    Unknown,
    Number,
    String,
    Boolean,
    Void,
    Object(Vec<(String, TypeKind)>),
    InBuilt(FnKind),
    Function,
    Any,
}


#[derive(Debug, Clone, PartialEq, PartialOrd, Hash, serde::Serialize, serde::Deserialize)]
pub enum FnKind {
    // ! only use for macros node creation
    Stub,

    Is,
    And,
    Or,

    Eq,
    Add,
    Mod,
    Mul,

    Call,
    Return,
}

impl ToString for FnKind {
    fn to_string(&self) -> String {
        match self {
            FnKind::Stub => "Stub".to_string(),
            FnKind::Is => "Is".to_string(),
            FnKind::And => "And".to_string(),
            FnKind::Or => "Or".to_string(),
            FnKind::Eq => "Eq".to_string(),
            FnKind::Add => "Add".to_string(),
            FnKind::Mod => "Mod".to_string(),
            FnKind::Mul => "Mul".to_string(),
            FnKind::Call => "Call".to_string(),
            FnKind::Return => "Return".to_string(),
        }
    }
}
