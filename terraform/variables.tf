variable "nodos" {
  description = "Nombre del nodo => puerto en tu Windows"
  type        = map(number)
  default = {
    web1 = 8081
    web2 = 8082
    web3 = 8083
  }
}
