output "urls" {
  value = { for k, c in docker_container.nodo : k => "http://localhost:${c.ports[0].external}" }
}
