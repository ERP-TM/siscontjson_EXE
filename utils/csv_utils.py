# db/csv_utils.py
# helpers
from config import get_output_dir, PAGINATION_THRESHOLD, \
    DEFAULT_PAGE_SIZE
import os


def save_csv_file(content, namefile:str):
    try:
        output_dir = get_output_dir()
        if not output_dir:
            raise ValueError("get_output_dir() devolvió una ruta vacía o nula")

        os.makedirs(output_dir, exist_ok=True)

        if not namefile:
            raise ValueError("namefile no puede ser None")
        
        output_path = os.path.join(output_dir, f"{namefile}")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
            #json.dump(content, f, indent=4, ensure_ascii=False)

        print(f"✅ CSV guardado en: {output_path}")  # Para depuración directa
        return output_path

    except Exception as e:
        print(f"❌ Error al guardar el CSV: {e}")
        raise