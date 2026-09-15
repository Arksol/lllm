from app.llm.base import Citation
from app.rag.chunker import Chunk
from app.rag.citations import verify

CHUNK = Chunk(
    file_path="app/servicio.py",
    start_line=10,
    end_line=14,
    text="def procesar(dato):\n    return dato.strip()",
)


def test_acepta_una_cita_que_existe_en_el_fragmento():
    cita = Citation(text="return dato.strip()", file_path="app/servicio.py", start_line=10, end_line=14)
    assert len(verify([cita], [CHUNK])) == 1


def test_descarta_una_cita_inventada():
    cita = Citation(text="return borrar_todo()", file_path="app/servicio.py", start_line=10, end_line=14)
    assert verify([cita], [CHUNK]) == []


def test_descarta_citas_a_archivos_que_no_se_enviaron():
    cita = Citation(text="algo", file_path="otro.py", start_line=1, end_line=2)
    assert verify([cita], [CHUNK]) == []


def test_no_repite_la_misma_cita():
    cita = Citation(text="return dato.strip()", file_path="app/servicio.py", start_line=10, end_line=14)
    assert len(verify([cita, cita], [CHUNK])) == 1
