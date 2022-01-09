use std::collections::HashMap;
use std::io::BufReader;
use std::fs::File;
use quick_xml as qxml;
use qxml::{Reader, events::Event};

struct Way {
    nodes : Vec<u64>,
}

impl Way {
    fn new() -> Way{
        Way {nodes : Vec::new()}
    }
    fn push(&mut self, value: u64) {
        self.nodes.push(value);
    }
}

pub fn load_map(){

    let mut nodehash = HashMap::<u64, [f32;2]>::new();
    let mut wayvec = Vec::<Way>::new();

    let mut reader = Reader::from_file("map.osm").unwrap();
    reader.trim_text(true);

    let mut buf = Vec::new();
    let mut wbuf = Vec::new();//buffer for way parsing
    
    //note we expect all nodes before ways
    loop {
        match reader.read_event(&mut buf) {

            Ok(Event::Start(ref e)) => {
                match e.name() {
                    b"node" => {
                        let node = xml_node(e);
                        nodehash.insert(node.0, node.1);
                        ()},
                    b"way" => {
                        let way = xml_way(&mut reader, &mut wbuf, e);
                        wayvec.push(way);
                        ()},
                    _ => {()},
                }
            },

            Ok(Event::Empty(ref e)) => {
                match e.name() {
                    b"node" => {
                        let node = xml_node(e);
                        nodehash.insert(node.0, node.1);
                        ()},
                    _ => {()},
                }
            },
           
            Ok(Event::Eof) => break, 
            Err(e) => panic!("Error at position {}: {:?}", reader.buffer_position(), e),
            _ => (), 
        }
    }
   println!("wayvec {}", wayvec.len()); 
   println!("nodehash {}", nodehash.keys().len()); 
}

fn xml_node(e : &qxml::events::BytesStart) -> (u64, [f32;2]){
    let aiter = e.attributes(); //itterator over attributes

    let mut node : (u64, [f32;2]) = (0,[0.0,0.0]);
    for attr in aiter{
        let attr = attr.unwrap();
        match attr.key {
            b"id" => {node.0 = lexical::parse::<u64, _>(attr.value).unwrap();},
            b"lat" => {node.1[0] = lexical::parse::<f32, _>(attr.value).unwrap();},
            b"lon" => {node.1[1] = lexical::parse::<f32, _>(attr.value).unwrap();},
            _ => {},
        }

    }
    return node;
}

//should probably use Text(BytesText<'a>) event
fn xml_nd(e : &qxml::events::BytesStart) -> u64{
    let aiter = e.attributes(); //itterator over attributes

    let mut nd : u64 = 0;
    for attr in aiter{
        let attr = attr.unwrap();
        match attr.key {
            b"nd" => {nd = lexical::parse::<u64, _>(attr.value).unwrap();},
            _ => {},
        }
    }
    return nd;
}

fn xml_way(r : &mut Reader<BufReader<File>>, mut buf : &mut Vec<u8>, e : &qxml::events::BytesStart) -> Way{
    let mut way = Way::new();
    
    let nm = e.name();
    loop {
        match r.read_event(&mut buf) {

            Ok(Event::Start(ref e)) => {

                match e.name() {
                    b"nd" => {
                        let nd = xml_nd(e);
                        way.push(nd);
                        ()},
                    _ => {()},
                }
            },
        
            Ok(Event::End(ref e)) => {
                match e.name() {
                    nm => break,
                    _ => (),
                }
            },

            // Ok(Event::Eof) => break, //we don't expect the file to end before the child is closed
            Err(e) => panic!("Error at position {}: {:?}", r.buffer_position(), e),
            _ => (), 
        }
    } 
    return Way::new();
}
