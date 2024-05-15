import json
from unittest.mock import patch
import os
from pathlib import Path
import shutil

from verinfast.agent import Agent
from verinfast.config import Config
from verinfast.utils.utils import DebugLog
import verinfast.user
from verinfast.dependencies.walk import walk
from verinfast.dependencies.walkers.classes import Entry

file_path = Path(__file__)
test_folder = file_path.parent
docker_folder = test_folder.joinpath('fixtures/docker')
results_dir = test_folder.joinpath("results").absolute()
composer_config_path = str(test_folder.joinpath('composer.yaml').absolute())


def logger(msg, **kwargs):
    print(msg)
    print(kwargs)


def test_dockerfile_exists():
    docker_file_path = docker_folder.joinpath('Dockerfile')
    assert Path.exists(docker_file_path)


def test_walk():
    output_path = walk(
        path=test_folder,
        output_file="./dependencies.json",
        logger=logger
        )
    with open(output_path) as output_file:
        output = json.load(output_file)
        assert len(output) >= 1
        first_dep = output[0]
        assert first_dep['name'] == 'simple-test-package'
    return None


def test_entity():
    output_path = walk(
        path=test_folder,
        output_file="./dependencies.json",
        logger=logger
    )
    with open(output_path) as output_file:
        output = json.load(output_file)
        assert len(output) >= 1
        first_dep = output[0]
        e = Entry(**first_dep)
        assert e.license == "ISC"
        found_Cosmos = False
        for d in output:
            if d["name"] == "Microsoft.Azure.Cosmos":
                found_Cosmos = True
                assert d["license"] == "https://aka.ms/netcoregaeula"
        assert found_Cosmos

    return None


def test_ruby():
    output_path = walk(
        path=test_folder,
        output_file="./dependencies.json",
        logger=logger
    )
    with open(output_path) as output_file:
        output = json.load(output_file)
        assert len(output) >= 1
        first_dep = output[0]
        e = Entry(**first_dep)
        assert e.license == "ISC"
        found_rubocop = False
        for d in output:
            if d["name"] == "rubocop-ast":
                found_rubocop = True
                assert d["specifier"] == "*"
        assert found_rubocop
        found_aasm = False
        for d in output:
            if d["name"] == "aasm":
                found_aasm = True
                assert d["specifier"] == "*"
        assert found_aasm
        found_bad_source_type = False
        found_source_single_quote = False
        for d in output:
            if type(d["source"]) is dict:
                found_bad_source_type = True
            elif d["source"].find("'") != -1:
                found_source_single_quote = True
        assert not found_bad_source_type
        assert not found_source_single_quote

    return None


def test_python():
    output_path = walk(
        path=test_folder,
        output_file="./dependencies.json",
        logger=logger
    )
    with open(output_path) as output_file:
        output = json.load(output_file)
        assert len(output) >= 1
        first_dep = output[0]
        e = Entry(**first_dep)
        assert e.license == "ISC"
        found_azure_identity = False
        for d in output:
            if d["name"] == "azure-identity":
                found_azure_identity = True
                assert d["source"] == "pip"
        assert found_azure_identity
        found_azure_core = False
        for d in output:
            if d["name"] == "azure-core":
                found_azure_core = True
                assert d["source"] == "pip"
        assert found_azure_core

    return None


def test_docker():
    output_path = walk(
        path=docker_folder,
        output_file="./dependencies.json",
        logger=logger
    )
    with open(output_path) as output_file:
        output = json.load(output_file)
        assert len(output) >= 1
        # first_dep = output[0]
        # e = Entry(**first_dep)
        # assert e.license == "ISC"
        found_ubuntu_base_image = False
        for d in output:
            if d["name"] == "ubuntu":
                found_ubuntu_base_image = True
                assert d["specifier"] == "trusty"
                assert d["source"] == "Dockerfile"
        assert found_ubuntu_base_image

    return None

def test_composer():
    output_path = walk(
        path=test_folder,
        output_file="./dependencies.json",
        logger=logger
    )
    with open(output_path) as output_file:
        output = json.load(output_file)
        assert len(output) >= 1

@patch('verinfast.user.__get_input__', return_value='y')
def test_composer_config(self):
    try:
        shutil.rmtree(results_dir)
    except Exception as e:
        print(e)
        pass
    os.makedirs(results_dir, exist_ok=True)
    agent = Agent()
    config = Config(composer_config_path)
    config.output_dir = results_dir
    print(agent.config.output_dir)
    agent.config = config
    agent.config.shouldUpload = True
    agent.debug = DebugLog(path=agent.config.output_dir, debug=False)
    agent.log = agent.debug.log
    print(agent.debug.logFile)
    agent.scan()
    assert Path(results_dir).exists() is True
