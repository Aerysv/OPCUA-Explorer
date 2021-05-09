import asyncio
from asyncua import Client
from asyncua import ua


async def browse_nodes_children(Server_URL, NodeId):
    """Explora los hijos directos del NodeId provisto

    Args:
        Server_URL (string): Dirección del servidor OPC-UA
        NodeId (string): Identificador del nodo de interés

    Returns:
        list: Nodos hijos
    """
    async with Client(url=Server_URL, timeout=60*60) as client:
        node = client.get_node(NodeId)
        children = await node.get_children()
        Nodes = [None]*len(children)
        Nodes_Names = [None]*len(children)
        Nodes_with_children = [0]*len(children)
        if children:
            for i, child in enumerate(children):
                browse_name = await child.read_display_name()
                Nodes[i] = child
                Nodes_Names[i] = browse_name.Text
                if await child.get_children():
                    Nodes_with_children[i] = 1
                # print(f'{Nodes[i]}\t|\t{Nodes_Names[i]}\t{Nodes_with_children[i]}')
        return [Nodes, Nodes_Names, Nodes_with_children]


async def obtener_root(Server_URL):
    """Obtiene el nodo raíz del servidor

    Args:
        Server_URL (string): Dirección del servidor OPC-UA

    Returns:
        string: Identificador del nodo OPC-UA
    """
    async with Client(url=Server_URL, timeout=60*60) as client:
        root_node = client.get_root_node()
        return str(root_node)


def main(Server_URL, NodeId):
    """LLama a la función encargada de explorar los hijos de NodeId

    Args:
        Server_URL (string): Dirección del servidor OPC-UA
        NodeId (string): Identificador del nodo de interés

    Returns:
        list: Nodos hijos
    """
    [Nodes, Nodes_Names, Nodes_with_children] = asyncio.run(
        browse_nodes_children(Server_URL, NodeId))
    return [Nodes, Nodes_Names, Nodes_with_children]


if __name__ == "__main__":
    Server_URL = 'opc.tcp://localhost:16703/'
    NodeId = 'ns=2;s=server_variables'
    main(Server_URL, NodeId)
