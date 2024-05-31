#[cfg(test)]
mod tests {

    use std::io::Read;

    use crate::{bidirectional::TypeCheck, bytecode::{ByteCode, VirtualMachine}, graph::Graph, lexer::{Lexer, Token}, node::Node, parser::Parser, typekind::TypeKind};

    #[test]
    fn test_basic_edge_conflicts() {

        let mut graph = Graph::new();

        let node_t1 = Node::new(TypeKind::Number);
        let node_t2 = Node::new(TypeKind::String);

        let node_t1_idx = graph.add_node(node_t1);
        let node_t2_idx = graph.add_node(node_t2);

        graph.add_edge(node_t1_idx, node_t2_idx);
        
        assert!(graph.check_edges(node_t1_idx).is_err());
        assert!(graph.check_edges(node_t2_idx).is_err());
    }

    #[test]
    fn test_basic_edge_no_conflicts() {

        let mut graph = Graph::new();

        let node_t1 = Node::new(TypeKind::String);
        let node_t2 = Node::new(TypeKind::String);

        let node_t1_idx = graph.add_node(node_t1);
        let node_t2_idx = graph.add_node(node_t2);

        graph.add_edge(node_t1_idx, node_t2_idx);

        assert!(graph.check_edges(node_t1_idx).is_ok());
        assert!(graph.check_edges(node_t2_idx).is_ok());
    }

    #[test]
    fn test_le_typekind_objects() {

        let obj_t1 = TypeKind::Object(vec![(String::from("x"), TypeKind::Number)]);
        let obj_t2 = TypeKind::Object(vec![(String::from("x"), TypeKind::Number)]);

        assert!(obj_t1 == obj_t2);
        assert!(obj_t1 <= obj_t2);

        let obj_t1 = TypeKind::Object(vec![(String::from("x"), TypeKind::Number)]);
        let obj_t2 = TypeKind::Object(vec![(String::from("x"), TypeKind::Number), (String::from("y"), TypeKind::String)]);

        assert!(obj_t1 < obj_t2);
        assert!(obj_t1 <= obj_t2);

    }

    #[test]
    fn test_parser() {

        let src = r#"
            class {
                foo: Function(x
                    Return(x))
                bar: Function(a, b
                    Eq(x Add(a b))
                    Return(x))
            }
        "#;
        let mut p = Parser::new(src);

        p.consume_whitespace();
        p.consume_keyword("class").unwrap();
        p.consume_whitespace();

        p.consume_brace('{').unwrap();
        p.consume_whitespace();

        let methods = p.parse_methods();
        assert_eq!(methods.len(), 2);

        let foo_lxr= Lexer::new(&methods[0]);
        assert_eq!(foo_lxr.len(), 1);
        assert_eq!(foo_lxr.arguments(), vec!["x".to_string()]);

        let bar_lxr = Lexer::new(&methods[1]);
        assert_eq!(bar_lxr.len(), 2);
        assert_eq!(bar_lxr.arguments(), vec!["a".to_string(), "b".to_string()]);
    }

    #[test]
    fn test_lexical_tokens_to_bytecode() {
        let mut buffer = Vec::new();
        let mut file = std::fs::File::open("./cmp_test/test_bytecode_lexer.cmp").unwrap();
        file.read_to_end(&mut buffer).unwrap();
        let vt: Vec<Token> = bincode::deserialize(&buffer).unwrap();

        let mut vm: VirtualMachine = VirtualMachine::new("foo".to_string(), vt);

        // let vm_byx: Vec<ByteCode> = vm.into();
        // assert_eq!(vm.bytecode_len(), 12);
    }

    #[test]
    fn test_integrated_complex() {
        let src = r#"
        class {
            Compose_f: Function(f
                Return(f))
            Compose_g: Function(g
                Return(g))
            Compose_x: Function(f,g,x
                Return(Call(f Call(g x))))
            Double: Function(x
                Return(Nary(Mul x 2)))
            Increment: Function(x
                Return(Nary(Add x 1)))
        }
        "#;

        let mut p = Parser::new(src);

        p.consume_whitespace();
        p.consume_keyword("class").unwrap();
        p.consume_whitespace();
        p.consume_brace('{').unwrap();
        p.consume_whitespace();

        let methods = p.parse_methods();
        assert_eq!(methods.len(), 5);

        let mut compose_f= Lexer::new(&methods[0]);
        assert_eq!(compose_f.len(), 1);
        assert_eq!(compose_f.arguments(), vec!["f".to_string()]);

        let mut compose_g = Lexer::new(&methods[1]);
        assert_eq!(compose_g.len(), 1);
        assert_eq!(compose_g.arguments(), vec!["g".to_string()]);

        let mut compose_x = Lexer::new(&methods[2]);
        assert_eq!(compose_x.len(), 1);
        assert_eq!(compose_x.arguments(), vec!["f".to_string(), "g".to_string(), "x".to_string()]);

        let mut double = Lexer::new(&methods[3]);
        assert_eq!(double.len(), 1);
        assert_eq!(double.arguments(), vec!["x".to_string()]);

        let mut increment = Lexer::new(&methods[4]);
        assert_eq!(increment.len(), 1);
        assert_eq!(increment.arguments(), vec!["x".to_string()]);

        compose_f.tokenize();
        compose_g.tokenize();
        compose_x.tokenize();
        double.tokenize();
        increment.tokenize();

        let compose_f_tokens: Vec<Token> = compose_f.clone().into();
        assert_eq!(compose_f_tokens.len(), 2);

        let compose_g_tokens: Vec<Token> = compose_g.clone().into();
        assert_eq!(compose_g_tokens.len(), 2);

        let compose_x_tokens: Vec<Token> = compose_x.clone().into();
        assert_eq!(compose_x_tokens.len(), 6);

        let double_tokens: Vec<Token> = double.clone().into();
        assert_eq!(double_tokens.len(), 4);

        let increment_tokens: Vec<Token> = increment.clone().into();
        assert_eq!(increment_tokens.len(), 4);

        let mut compose_f_vm: VirtualMachine = compose_f.clone().into();
        // compose_f_vm.to_bytecode();

        let mut compose_g_vm = VirtualMachine::new("Compose_g".to_string(), compose_g_tokens);
        // compose_g_vm.to_bytecode();

        let mut compose_x_vm = VirtualMachine::new("Compose_x".to_string(), compose_x_tokens);
        dbg!(&compose_x_vm);
        let compose_x_byc: Vec<ByteCode> = compose_x_vm.into();

        let mut double_vm = VirtualMachine::new("Double".to_string(), double_tokens);
        // double_vm.to_bytecode();

        let mut increment_vm = VirtualMachine::new("Increment".to_string(), increment_tokens);
        // increment_vm.to_bytecode();


    }

}
