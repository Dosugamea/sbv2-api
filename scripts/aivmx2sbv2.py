import onnx
import base64
import numpy as np
import json
import tarfile
import zstandard
import io
import sys

def convert_aivmx_to_sbv2(input_path, output_path):
    print(f"Loading {input_path}...")
    # Load the ONNX model
    model = onnx.load(input_path)

    # Extract metadata
    style_vectors_b64 = None
    new_metadata_props = []

    for prop in model.metadata_props:
        if prop.key == 'aivm_style_vectors':
            style_vectors_b64 = prop.value
        elif prop.key in ['aivm_manifest', 'aivm_hyper_parameters']:
            # Skip AIVM specific metadata to clean up the ONNX model
            pass
        else:
            new_metadata_props.append(prop)

    if style_vectors_b64 is None:
        raise ValueError("Error: The AIVMX file does not contain 'aivm_style_vectors' metadata.")

    # Update metadata to remove AIVM specific props
    del model.metadata_props[:]
    model.metadata_props.extend(new_metadata_props)

    print("Decoding style vectors...")
    # Decode style vectors
    style_bytes = base64.b64decode(style_vectors_b64)
    array = np.load(io.BytesIO(style_bytes))

    style_json = json.dumps({
        "data": array.tolist(),
        "shape": list(array.shape)
    }).encode("utf-8")

    print("Serializing ONNX model...")
    # Serialize ONNX model to bytes
    onnx_bytes = model.SerializeToString()

    version_bytes = b"1"

    print("Packing into tar archive...")
    # Create tar archive in memory
    tar_io = io.BytesIO()
    with tarfile.open(fileobj=tar_io, mode="w") as tar:
        def add_file(name, data):
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))

        add_file("version.txt", version_bytes)
        add_file("model.onnx", onnx_bytes)
        add_file("style_vectors.json", style_json)

    print("Compressing with zstandard...")
    # Compress with zstandard
    cctx = zstandard.ZstdCompressor(threads=-1, level=22)
    compressed_data = cctx.compress(tar_io.getvalue())

    print(f"Saving to {output_path}...")
    with open(output_path, "wb") as f:
        f.write(compressed_data)

    print(f"✨ Successfully converted {input_path} to {output_path}! ✨")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python aivmx2sbv2.py <input.aivmx> <output.sbv2>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        convert_aivmx_to_sbv2(input_file, output_file)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
