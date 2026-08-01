"""Neo4j knowledge graph schema constants for FurniCost.

Graph model (furniture factory):

    (:Product {product_id})                     products sold
    (:Component {component_id})                 sub-assemblies / parts
    (:Material {part_id})                       raw materials w/ unit_price
    (:Machine {machine_id})                     workstations w/ hourly_rate
    (:Operation {op_id})                        routing steps (hours, rates)
    (:Activity {activity_id})                   ABC overhead cost pools w/ driver_rate

    (n:Product|Component)-[:CONTAINS {quantity}]->(m:Product|Component)
    (n:Product|Component)-[:USES_MATERIAL {quantity, sequence}]->(:Material)
    (n:Product|Component)-[:REQUIRES {sequence}]->(:Operation)
    (n:Product|Component)-[:CONSUMES {quantity}]->(:Activity)
    (:Operation)-[:PERFORMED_ON]->(:Machine)
"""

PRODUCT = "Product"
COMPONENT = "Component"
MATERIAL = "Material"
MACHINE = "Machine"
OPERATION = "Operation"
ACTIVITY = "Activity"

CONTAINS = "CONTAINS"
USES_MATERIAL = "USES_MATERIAL"
REQUIRES = "REQUIRES"
CONSUMES = "CONSUMES"
PERFORMED_ON = "PERFORMED_ON"

# node id property per label (driver-facing key)
ID_PROPERTY: dict[str, str] = {
    PRODUCT: "product_id",
    COMPONENT: "component_id",
    MATERIAL: "part_id",
    MACHINE: "machine_id",
    OPERATION: "op_id",
    ACTIVITY: "activity_id",
}

NODE_LABELS = list(ID_PROPERTY)
