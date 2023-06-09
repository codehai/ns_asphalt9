import argparse

parser = argparse.ArgumentParser(description="NS Asphalt9 Tool.")
parser.add_argument("-c", "--config", type=str, help="自定义配置文件")

args = parser.parse_args()
print(args.config)
