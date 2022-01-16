use std::f32::consts::TAU as PI2;
use std::collections::HashMap;
use std::io::{Write,BufReader};
use std::fs::File;
use quick_xml as qxml;
use qxml::{Reader, events::Event};

use crate::renderer::{Line};

#[derive(Debug)]
pub struct Way {
    pub nodes : Vec<u64>,
}

impl Way {
    fn new() -> Way{
        Way {nodes : Vec::new()}
    }
    fn push(&mut self, value: u64) {
        self.nodes.push(value);
    }
}

pub fn tofile(fp :  &str, lines : Vec<Line>){

    let mut f = File::create(fp).unwrap();

    for line in lines{

        for flt in line.to{
            let bts = flt.to_ne_bytes();
            f.write(&bts).unwrap();
        }
        for flt in line.from{
            let bts = flt.to_ne_bytes();
            f.write(&bts).unwrap();
        }
        for flt in line.colour{
            let bts = flt.to_ne_bytes();
            f.write(&bts).unwrap();
        }
    }

}

pub fn format(segs : (Vec::<Way>,HashMap<u64, [f32;2]>)) -> Vec<Line>{
    let (ways, nodes) = segs;

    let mut lines = Vec::<Line>::new();

    for way in ways{
        let niter = way.nodes.windows(2);//get node ids 2 at a time
        for nodeids in niter{
            let toid = nodeids.get(0).unwrap();
            let fmid = nodeids.get(1).unwrap();
            let to : [f32;2] = nodes[toid];
            let from : [f32;2] = nodes[fmid];

            let colour = colourfunc(to,from);
            let width = widthfunc(to,from);

            let line : Line = Line {to,from,colour,width};

            lines.push(line);

        }


    }

    return lines;

}

fn colourfunc(to : [f32;2], from : [f32;2]) -> [f32;3]{
    let dlat = to[0] - from[0];
    let dlon = to[1] - from[1];
    
    let x = (to[0].to_radians()).cos() * dlon;
    let y = dlat;
    
    let ang = y.atan2(x);
    
    let h = (4.0*ang/PI2) % 1.0;
    let s = 0.6;
    let v = 1.0;
    return [h,s,v]
}

fn widthfunc(to : [f32;2], from : [f32;2]) -> f32{
    0.1
}

pub fn load_map(fp : &str) -> (Vec::<Way>,HashMap<u64, [f32;2]>){

    let mut nodehash = HashMap::<u64, [f32;2]>::new();
    let mut wayvec = Vec::<Way>::new();

    let mut reader = Reader::from_file(fp).unwrap();
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
    (wayvec,nodehash)
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


fn xml_nd(e : &qxml::events::BytesStart) -> u64{
    let aiter = e.attributes(); //itterator over attributes

    let mut nd : u64 = 0;
    for attr in aiter{
        let attr = attr.unwrap();
        match attr.key {
            b"ref" => {nd = lexical::parse::<u64, _>(attr.value).unwrap();},
            _ => {},
        }
    }
    return nd;
}

fn xml_way(r : &mut Reader<BufReader<File>>, mut buf : &mut Vec<u8>, es : &qxml::events::BytesStart) -> Way{
    let mut way = Way::new();
    
    let nm = es.name();
    loop {
        match r.read_event(&mut buf) {

            Ok(Event::Empty(ref e)) => {

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
    return way;
}
