use ceph_db::{graph::Graph, lexer::{Lexer, Token}, node::Node, parser::Parser, typekind::{FnKind, TypeKind}};

use std::io::Read;


fn main() {
    println!("Ceph DB!");

    let mut graph = Graph::new();

    // y = x + 123
    // Eq(y, Add(x, 123))

    let y_node = Node::new(TypeKind::Unknown);
    let x_node = Node::new(TypeKind::Unknown);
    let num_literal = Node::new(TypeKind::Number);
    let add_node = Node::new(TypeKind::InBuilt(FnKind::Add));
    let eq_node = Node::new(TypeKind::InBuilt(FnKind::Eq));

    let y_node_idx = graph.add_node(y_node);
    let x_node_idx = graph.add_node(x_node);
    let num_literal_idx = graph.add_node(num_literal);
    let add_node_idx = graph.add_node(add_node);
    let eq_node_idx = graph.add_node(eq_node);

    graph.get_node_mut(add_node_idx).unwrap().set_arguments(vec![x_node_idx, num_literal_idx]);
    graph.get_node_mut(eq_node_idx).unwrap().set_arguments(vec![y_node_idx, add_node_idx]);


    for i in 0..graph.len() {
        graph.type_check(i).unwrap();
    }

//    dbg!(&graph);

    let src = r#"
        class {
            foo: Function(x
                Return(x))
            bar: Function(a, b, c
                Eq(x Add(a b c))
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

    let mut bar_lxr = Lexer::new(&methods[1]);
    bar_lxr.tokenize();

    let bat_tok: Vec<Token> = bar_lxr.into();

    dbg!(bat_tok);

}
