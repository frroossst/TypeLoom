#[macro_export]
macro_rules! basal_types {
    ($nodes:expr) => {
        {
            use TypeKind::*;
            let variants = [
                Number, String, Boolean, Void, Object(Vec::new()), InBuilt(crate::typekind::FnKind::Stub), Function
            ];

            for variant in &variants {
                if *variant != Unknown && *variant != Any {
                    $nodes.push(Node::new(variant.clone()));
                }
            }
        }
    };
}
