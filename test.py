import yaml


if __name__ == '__main__':
    with open("file/sharding.yml") as f:
        x = yaml.load(f, yaml.FullLoader)
    print(len(x["shardingRule"].keys()))
