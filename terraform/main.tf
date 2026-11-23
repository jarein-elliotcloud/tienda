# La imagen base: un Ubuntu mínimo
resource "docker_image" "ubuntu" {
  name         = "ubuntu:24.04"
  keep_locally = true
}

# Una "máquina" por cada entrada del mapa
resource "docker_container" "nodo" {
  for_each = var.nodos

  name    = "tienda-${each.key}"
  image   = docker_image.ubuntu.image_id
  command = ["sleep", "infinity"] # sin esto, el contenedor arranca y se apaga

  ports {
    internal = 80         # nginx dentro del contenedor
    external = each.value # puerto en tu máquina
  }
}

# El inventario de Ansible, generado con los datos REALES de los contenedores
resource "local_file" "inventario" {
  filename        = "${path.module}/../ansible/inventario.ini"
  file_permission = "0644"
  content = templatefile("${path.module}/inventario.tftpl", {
    nodos = {
      for k, c in docker_container.nodo :
      k => { contenedor = c.name, puerto = c.ports[0].external }
    }
  })
}
