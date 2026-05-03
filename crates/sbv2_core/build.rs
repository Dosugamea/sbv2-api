use dirs::home_dir;
use std::env;
use std::fs;
use std::io::copy;
use std::path::PathBuf;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("cargo:rerun-if-changed=build.rs");
    Ok(())
}
