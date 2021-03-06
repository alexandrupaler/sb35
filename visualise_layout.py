'''
    This class takes a layout
'''
import layout as la
import operationcollection as opc

class VisualiseLayout:
    def __init__(self):
        print("visual debug")

    def get_color(self, op_type):
        if op_type == opc.OperationTypes.NOOP:
            return "white"
        elif op_type == opc.OperationTypes.USE_DISTILLATION:
            return "magenta"
        elif op_type == opc.OperationTypes.USE_QUBIT:
            return "red"
        elif op_type == opc.OperationTypes.USE_ANCILLA:
            return "yellow"
        elif op_type == opc.OperationTypes.USE_S_GATE:
            return "green"
        elif op_type == opc.OperationTypes.MOVE_PATCH:
            return "orange"
        elif op_type == opc.OperationTypes.HADAMARD_QUBIT:
            return "cyan"
        elif op_type == opc.OperationTypes.MX_QUBIT:
            return "cyan"
        elif op_type == opc.OperationTypes.MZ_QUBIT:
            return "cyan"

    def remove_if_in_distillery_core(self, layout, i, j, t):
        # use this cube only if at least one neighbouring coordinate is not of the same type
        # effectively removes core of large boxes... eases the viualisation
        same_type_nghs = 0

        for mi in range(-1, 2):
            for mj in range(-1, 2):
                for mt in range(-1, 2):
                    if (mi != 0) and (mj != 0) and (mt != 0):
                        ni = i + mi
                        nj = j + mj
                        nt = t + mt

                        valid_coord = ni in range(layout.get_isize())
                        valid_coord = valid_coord and (nj in range(layout.get_jsize()))
                        valid_coord = valid_coord and (nt in range(layout.get_tsize()))

                        if valid_coord and (layout.coordinates[ni][nj][nt] is not None):
                            n_op_id = layout.coordinates[ni][nj][nt].operations[0]
                            n_op_type = layout.operations_dictionary[n_op_id].op_type

                            if n_op_type == opc.OperationTypes.USE_DISTILLATION:
                                same_type_nghs += 1

        # print(same_type_nghs)
        return (same_type_nghs == 8)



    def visualise_cube(self, layout, remove_noop):
        json2 = {"nodes": [], "links": []}

        # simple type checking
        if not isinstance(layout, la.CubeLayout):
            print("ERROR: This is not a layout!\n")
            return

        for i in range(layout.get_isize()):
            for j in range(layout.get_jsize()):
                for t in range(layout.get_tsize()):

                    ops_collection = layout.coordinates[i][j][t]

                    # take each operation from the collection and make a cube out of it

                    # filter
                    if ops_collection is None:
                        continue

                    for op_id in ops_collection.operations:
                        op_type = layout.operations_dictionary[op_id].op_type

                        if op_type == opc.OperationTypes.USE_DISTILLATION:
                            if self.remove_if_in_distillery_core(layout, i, j, t):
                                # this cell should not be considered
                                break

                        cell_id = layout.get_cell_id(i, j, t)
                        color = self.get_color(op_type)

                        decorator = "."
                        dec_set = [opc.OperationTypes.HADAMARD_QUBIT,
                                   opc.OperationTypes.MX_QUBIT,
                                   opc.OperationTypes.MZ_QUBIT]
                        if ops_collection.get_zero_length_ops(layout.operations_dictionary) in dec_set:
                            # force all decorators to behave the same
                            # hard coded ...
                            decorator = "H"

                        # # filter
                        # if ops_collection.has_single_noop(layout.operations_dictionary) and remove_noop:
                        #     continue

                        sides = ops_collection.sides_integer_value

                        # sides = 60
                        # # when default this means that the volume is not used
                        # # ancillas do not rotate their X or Z?
                        # if op_type in [opc.OperationTypes.NOOP, opc.OperationTypes.USE_ANCILLA]:
                        #     sides = 63

                        node_value = {"id": cell_id,
                                      "fy": i, "fx": j, "fz": t,
                                      "c": color,
                                      "op": str(op_type) + "_" + str(op_id),
                                      "s": sides,
                                      "d": decorator}
                        json2["nodes"].append(node_value)

        # for each operation in the collection of 3D cells
        # determine which operations touch which
        for op_id in layout.operations_dictionary:
            operation = layout.operations_dictionary[op_id]
            # for touch_id in operation["touches"]:
            for touch_id in operation.touches:
                touch_link = {"source": touch_id, "target": operation.touches[touch_id], "c": "blue"}
                json2["links"].append(touch_link)

        return json2
