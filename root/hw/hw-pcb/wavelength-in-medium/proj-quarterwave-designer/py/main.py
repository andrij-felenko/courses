# Приклад генерації відрізка трансформатора в KiCad pcbnew
import pcbnew

def place_microstrip_transformer(board, start_pos, width_mm, length_mm, layer_name="F.Cu"):
    layer_id = board.GetLayerID(layer_name)
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(start_pos)
    end_pos = pcbnew.VECTOR2I(start_pos.x + int(length_mm * 1e6), start_pos.y)
    track.SetEnd(end_pos)
    track.SetWidth(int(width_mm * 1e6))
    track.SetLayer(layer_id)
    board.Add(track)
