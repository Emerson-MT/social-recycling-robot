#!/usr/bin/env python3
"""
Script para convertir modelos ONNX a formato HEF para Hailo-8L

Uso:
    # Convertir un modelo específico
    python convert_onnx_to_hef.py --input model.onnx --output models/

    # Convertir todos los modelos en una carpeta
    python convert_onnx_to_hef.py --input-dir backups/ --output models/

    # Con datos de calibración personalizados
    python convert_onnx_to_hef.py --input model.onnx --calib-path my_images/ --classes 4
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def check_dependencies():
    """Verifica que las herramientas necesarias estén instaladas"""
    print("🔍 Verificando dependencias...")

    # Verificar hailomz
    try:
        result = subprocess.run(
            ["hailomz", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"  ✅ hailomz: {result.stdout.strip()}")
        else:
            print("  ❌ hailomz no funciona correctamente")
            return False
    except FileNotFoundError:
        print("  ❌ hailomz no encontrado")
        print("\n💡 Instala con: pip install hailo-model-zoo")
        return False
    except subprocess.TimeoutExpired:
        print("  ⚠️  hailomz no responde")
        return False

    # Verificar hailortcli (opcional pero recomendado)
    try:
        result = subprocess.run(
            ["hailortcli", "fw-control", "identify"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("  ✅ Hailo device detectado")
        else:
            print("  ⚠️  Hailo device no detectado (compilación aún posible)")
    except FileNotFoundError:
        print("  ⚠️  hailortcli no encontrado (compilación aún posible)")

    return True


def compile_onnx_to_hef(
    onnx_path: Path,
    output_dir: Path,
    calib_path: Path = None,
    num_classes: int = 4,
    hw_arch: str = "hailo8l",
    performance: bool = True,
    yaml_config: Path = None
):
    """
    Compila un modelo ONNX a formato HEF para Hailo

    Args:
        onnx_path: Ruta al archivo ONNX
        output_dir: Directorio de salida para el HEF
        calib_path: Ruta a imágenes de calibración
        num_classes: Número de clases del modelo
        hw_arch: Arquitectura de hardware (hailo8l, hailo8)
        performance: Optimizar para rendimiento vs precisión
        yaml_config: Archivo YAML de configuración personalizado
    """
    print(f"\n{'='*60}")
    print(f"📦 Compilando: {onnx_path.name}")
    print(f"{'='*60}")

    # Verificar que el archivo ONNX existe
    if not onnx_path.exists():
        print(f"❌ Error: Archivo no encontrado: {onnx_path}")
        return False

    # Crear directorio de salida si no existe
    output_dir.mkdir(parents=True, exist_ok=True)

    # Nombre del archivo de salida
    hef_name = onnx_path.stem + ".hef"
    hef_path = output_dir / hef_name

    # Verificar si ya existe
    if hef_path.exists():
        response = input(f"⚠️  {hef_name} ya existe. ¿Sobrescribir? (s/N): ")
        if response.lower() not in ['s', 'y', 'si', 'yes']:
            print("⏭️  Omitiendo...")
            return True

    # Construir comando
    cmd = [
        "hailomz", "compile",
        "--ckpt", str(onnx_path),
        "--hw-arch", hw_arch,
        "--classes", str(num_classes),
    ]

    # Agregar path de calibración si se proporciona
    if calib_path and calib_path.exists():
        cmd.extend(["--calib-path", str(calib_path)])
    else:
        print("⚠️  No se proporcionó ruta de calibración, usando valores por defecto")

    # Agregar configuración YAML si se proporciona
    if yaml_config and yaml_config.exists():
        cmd.extend(["--yaml", str(yaml_config)])

    # Optimización
    if performance:
        cmd.append("--performance")
    else:
        cmd.append("--accuracy")

    # Directorio de salida
    cmd.extend(["--output-dir", str(output_dir)])

    print(f"\n🔧 Comando: {' '.join(cmd)}\n")
    print("⏳ Compilando... (esto puede tardar 5-15 minutos)\n")

    try:
        # Ejecutar compilación
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutos máximo
        )

        # Mostrar output
        if result.stdout:
            print(result.stdout)

        if result.returncode == 0:
            print(f"\n✅ Compilación exitosa!")
            print(f"📁 Archivo generado: {hef_path}")

            # Mostrar tamaño del archivo
            if hef_path.exists():
                size_mb = hef_path.stat().st_size / (1024 * 1024)
                print(f"📊 Tamaño: {size_mb:.2f} MB")

            return True
        else:
            print(f"\n❌ Error en compilación:")
            if result.stderr:
                print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("\n❌ Error: Compilación excedió 30 minutos")
        return False
    except KeyboardInterrupt:
        print("\n⚠️  Compilación cancelada por usuario")
        return False
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Convertir modelos ONNX a formato HEF para Hailo-8L",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Convertir un modelo
  %(prog)s --input model.onnx --output models/

  # Convertir todos los ONNX de una carpeta
  %(prog)s --input-dir backups/ --output models/

  # Con calibración personalizada
  %(prog)s --input model.onnx --calib-path images/ --classes 4

  # Optimizar para precisión en vez de velocidad
  %(prog)s --input model.onnx --output models/ --accuracy
        """
    )

    # Argumentos de entrada
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--input",
        type=Path,
        help="Archivo ONNX individual a convertir"
    )
    input_group.add_argument(
        "--input-dir",
        type=Path,
        help="Directorio con archivos ONNX (convierte todos)"
    )

    # Argumentos de salida
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("models"),
        help="Directorio de salida para archivos HEF (default: models/)"
    )

    # Argumentos de configuración
    parser.add_argument(
        "--calib-path",
        type=Path,
        help="Ruta a imágenes de calibración (opcional)"
    )
    parser.add_argument(
        "--classes",
        type=int,
        default=4,
        help="Número de clases del modelo (default: 4)"
    )
    parser.add_argument(
        "--hw-arch",
        choices=["hailo8l", "hailo8"],
        default="hailo8l",
        help="Arquitectura de hardware (default: hailo8l)"
    )
    parser.add_argument(
        "--yaml",
        type=Path,
        help="Archivo de configuración YAML personalizado"
    )

    # Optimización
    optimization = parser.add_mutually_exclusive_group()
    optimization.add_argument(
        "--performance",
        action="store_true",
        default=True,
        help="Optimizar para velocidad (default)"
    )
    optimization.add_argument(
        "--accuracy",
        action="store_true",
        help="Optimizar para precisión"
    )

    args = parser.parse_args()

    # Banner
    print("\n" + "="*60)
    print("🚀 Conversor ONNX → HEF para Hailo")
    print("="*60)

    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)

    # Determinar archivos a procesar
    onnx_files = []
    if args.input:
        if not args.input.suffix == ".onnx":
            print(f"❌ Error: {args.input} no es un archivo ONNX")
            sys.exit(1)
        onnx_files = [args.input]
    elif args.input_dir:
        if not args.input_dir.is_dir():
            print(f"❌ Error: {args.input_dir} no es un directorio")
            sys.exit(1)
        onnx_files = list(args.input_dir.glob("*.onnx"))
        if not onnx_files:
            print(f"❌ Error: No se encontraron archivos ONNX en {args.input_dir}")
            sys.exit(1)

    print(f"\n📋 Archivos a procesar: {len(onnx_files)}")
    for f in onnx_files:
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  • {f.name} ({size_mb:.2f} MB)")

    # Confirmar
    if len(onnx_files) > 1:
        response = input(f"\n¿Continuar con la conversión? (S/n): ")
        if response.lower() in ['n', 'no']:
            print("❌ Cancelado por usuario")
            sys.exit(0)

    # Procesar cada archivo
    success_count = 0
    performance_mode = not args.accuracy

    for onnx_file in onnx_files:
        success = compile_onnx_to_hef(
            onnx_path=onnx_file,
            output_dir=args.output,
            calib_path=args.calib_path,
            num_classes=args.classes,
            hw_arch=args.hw_arch,
            performance=performance_mode,
            yaml_config=args.yaml
        )
        if success:
            success_count += 1

    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN")
    print("="*60)
    print(f"✅ Exitosos: {success_count}/{len(onnx_files)}")
    print(f"❌ Fallidos:  {len(onnx_files) - success_count}/{len(onnx_files)}")

    if success_count > 0:
        print(f"\n📁 Archivos generados en: {args.output.absolute()}")
        print("\n💡 Próximo paso:")
        print(f"   1. Copiar archivos HEF a: src/robot_project/models/")
        print(f"   2. Actualizar config.json con el nombre del modelo")
        print(f"   3. Ejecutar: python main.py")

    sys.exit(0 if success_count == len(onnx_files) else 1)


if __name__ == "__main__":
    main()
