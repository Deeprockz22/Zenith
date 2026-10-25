use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};

fn response(status: &str, content_type: &str, body: &str) -> String {
    format!(
        "HTTP/1.1 {status}\r\nContent-Type: {content_type}\r\nContent-Length: {}\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n{body}",
        body.len()
    )
}

fn handle(mut stream: TcpStream) {
    let mut request = [0_u8; 1024];
    let Ok(size) = stream.read(&mut request) else { return };
    let request = String::from_utf8_lossy(&request[..size]);
    let path = request
        .lines()
        .next()
        .and_then(|line| line.split_whitespace().nth(1))
        .unwrap_or("/");

    let (status, content_type, body) = match path {
        "/health" => ("200 OK", "application/json", r#"{"status":"ok","engine":"rust"}"#),
        _ => ("404 Not Found", "application/json", r#"{"error":"not found"}"#),
    };
    let _ = stream.write_all(response(status, content_type, body).as_bytes());
}

fn main() -> std::io::Result<()> {
    let address = std::env::var("ZENITH_RUST_ADDR")
        .unwrap_or_else(|_| "127.0.0.1:5051".to_string());
    let listener = TcpListener::bind(address)?;
    eprintln!("Zenith Rust control plane listening on {}", listener.local_addr()?);
    for stream in listener.incoming() {
        if let Ok(stream) = stream {
            handle(stream);
        }
    }
    Ok(())
}
