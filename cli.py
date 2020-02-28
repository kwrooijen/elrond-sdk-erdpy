import os
import logging

from argparse import ArgumentParser
from erdpy.proxy.tx_types import TxTypes
from erdpy import config, dependencies, errors, flows, nodedebug, projects
from erdpy._version import __version__

logger = logging.getLogger("cli")


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = setup_parser()
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
    else:
        args.func(args)


def setup_parser():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    parser.add_argument('-v', '--version', action='version', version=f"erdpy {__version__}")

    install_parser = subparsers.add_parser("install")
    choices = ["C_BUILDCHAIN", "SOL_BUILDCHAIN",
               "RUST_BUILDCHAIN", "NODE_DEBUG"]
    install_parser.add_argument("group", choices=choices)
    install_parser.set_defaults(func=install)

    create_parser = subparsers.add_parser("new")
    create_parser.add_argument("name")
    create_parser.add_argument("--template", required=True)
    create_parser.add_argument("--directory", type=str)
    create_parser.set_defaults(func=create)

    templates_parser = subparsers.add_parser("templates")
    templates_parser.add_argument("--json", action="store_true")
    templates_parser.set_defaults(func=list_templates)

    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("project", nargs='?', default=os.getcwd())
    build_parser.add_argument("--debug", action="store_true")
    build_parser.set_defaults(func=build)

    deploy_parser = subparsers.add_parser("deploy")
    # TODO: path to project or path to bytecode (hex.arwen).
    deploy_parser.add_argument("project", nargs='?', default=os.getcwd())
    deploy_parser.add_argument("--proxy", required=True)
    deploy_parser.add_argument("--owner", required=True)
    deploy_parser.add_argument("--pem", required=True)
    deploy_parser.add_argument("--arguments", nargs='+')
    deploy_parser.add_argument("--gas-price", default=config.DEFAULT_GASPRICE)
    deploy_parser.add_argument("--gas-limit", default=config.DEFAULT_GASLIMIT)
    deploy_parser.set_defaults(func=deploy)

    call_parser = subparsers.add_parser("call")
    call_parser.add_argument("contract")
    call_parser.add_argument("--proxy", required=True)
    call_parser.add_argument("--caller", required=True)
    call_parser.add_argument("--pem", required=True)
    call_parser.add_argument("--function", required=True)
    call_parser.add_argument("--arguments", nargs='+')
    call_parser.add_argument("--gas-price", default=config.DEFAULT_GASPRICE)
    call_parser.add_argument("--gas-limit", default=config.DEFAULT_GASLIMIT)
    call_parser.set_defaults(func=call)

    query_parser = subparsers.add_parser("query")
    query_parser.add_argument("contract")
    query_parser.add_argument("--proxy", required=True)
    query_parser.add_argument("--function", required=True)
    query_parser.add_argument("--arguments", nargs='+')
    query_parser.set_defaults(func=query)

    get_account_parser = subparsers.add_parser("get_account")
    get_account_parser.add_argument("--proxy", required=True)
    get_account_parser.add_argument("--address", required=True)
    get_account_parser.add_argument("--balance", required=False, nargs='?', const=True, default=False)
    get_account_parser.add_argument("--nonce", required=False, nargs='?', const=True, default=False)
    get_account_parser.set_defaults(func=get_account)

    get_num_shard_parser = subparsers.add_parser("get_num_shards")
    get_num_shard_parser.add_argument("--proxy", required=True)
    get_num_shard_parser.set_defaults(func=get_num_shards)

    get_last_block_nonce_parser = subparsers.add_parser("get_last_block_nonce")
    get_last_block_nonce_parser.add_argument("--proxy", required=True)
    get_last_block_nonce_parser.add_argument("--shard-id", required=True)
    get_last_block_nonce_parser.set_defaults(func=get_last_block_nonce)

    get_gas_price_parser = subparsers.add_parser("get_gas_price")
    get_gas_price_parser.add_argument("--proxy", required=True)
    get_gas_price_parser.set_defaults(func=get_gas_price)

    get_chain_id_parser = subparsers.add_parser("get_chain_id")
    get_chain_id_parser.add_argument("--proxy", required=True)
    get_chain_id_parser.set_defaults(func=get_chain_id)

    get_transaction_cost_parser = subparsers.add_parser("get_transaction_cost")
    tx_types = [TxTypes.SC_CALL, TxTypes.MOVE_BALANCE, TxTypes.SC_DEPLOY]
    get_transaction_cost_parser.add_argument("tx_type", choices=tx_types)
    get_transaction_cost_parser.add_argument("--proxy", required=True)
    get_transaction_cost_parser.add_argument("--data", required=False)
    get_transaction_cost_parser.add_argument("--sc-address", required=False)
    get_transaction_cost_parser.add_argument("--path", required=False)
    get_transaction_cost_parser.add_argument("--function", required=False)
    get_transaction_cost_parser.add_argument("--arguments", nargs='+', required=False)
    get_transaction_cost_parser.set_defaults(func=get_transaction_cost)

    node_parser = subparsers.add_parser("nodedebug")
    group = node_parser.add_mutually_exclusive_group()
    group.add_argument('--stop', action='store_true')
    group.add_argument('--restart', action='store_true', default=True)
    node_parser.set_defaults(func=do_nodedebug)

    test_parser = subparsers.add_parser("test")
    test_parser.add_argument("project", nargs='?', default=os.getcwd())
    test_parser.add_argument("--wildcard", default="*")
    test_parser.set_defaults(func=run_tests)

    return parser


def install(args):
    group = args.group

    try:
        dependencies.install_group(group, overwrite=True)
    except errors.KnownError as err:
        logger.fatal(err)


def list_templates(args):
    json = args.json

    try:
        projects.list_project_templates(json)
    except errors.KnownError as err:
        logger.fatal(err)


def create(args):
    name = args.name
    template = args.template
    directory = args.directory

    try:
        projects.create_from_template(name, template, directory)
    except errors.KnownError as err:
        logger.fatal(err)


def build(args):
    project = args.project
    debug = args.debug

    try:
        projects.build_project(project, debug)
    except errors.KnownError as err:
        logger.fatal(err)


def deploy(args):
    project = args.project
    owner = args.owner
    pem = args.pem
    proxy = args.proxy
    arguments = args.arguments
    gas_price = args.gas_price
    gas_limit = args.gas_limit

    try:
        flows.deploy_smart_contract(project, owner, pem, proxy, arguments, gas_price, gas_limit)
    except errors.KnownError as err:
        logger.fatal(err)


def call(args):
    contract = args.contract
    caller = args.caller
    pem = args.pem
    proxy = args.proxy
    function = args.function
    arguments = args.arguments
    gas_price = args.gas_price
    gas_limit = args.gas_limit

    try:
        flows.call_smart_contract(contract, caller, pem, proxy, function, arguments, gas_price, gas_limit)
    except errors.KnownError as err:
        logger.fatal(err)


def query(args):
    contract = args.contract
    proxy = args.proxy
    function = args.function
    arguments = args.arguments

    try:
        flows.query_smart_contract(contract, proxy, function, arguments)
    except errors.KnownError as err:
        logger.fatal(err)


def get_account(args):
    proxy = args.proxy
    address = args.address
    try:
        if args.balance:
            flows.get_account_balance(proxy, address)
        elif args.nonce:
            flows.get_account_nonce(proxy, address)
        else:
            flows.get_account(proxy, address)
    except errors.KnownError as err:
        logger.fatal(err)


def get_transaction_cost(args):
    try:
        flows.get_transaction_cost(args)
    except errors.KnownError as err:
        logger.fatal(err)


def get_num_shards(args):
    proxy = args.proxy

    try:
        flows.get_num_shards(proxy)
    except errors.KnownError as err:
        logger.fatal(err)


def get_last_block_nonce(args):
    proxy = args.proxy
    shard_id = args.shard_id

    try:
        flows.get_last_block_nonce(proxy, shard_id)
    except errors.KnownError as err:
        logger.fatal(err)


def get_gas_price(args):
    proxy = args.proxy

    try:
        flows.get_gas_price(proxy)
    except errors.KnownError as err:
        logger.fatal(err)


def get_chain_id(args):
    proxy = args.proxy

    try:
        flows.get_chain_id(proxy)
    except errors.KnownError as err:
        logger.fatal(err)


def do_nodedebug(args):
    stop = args.stop
    restart = args.restart

    try:
        if restart:
            nodedebug.stop()
            nodedebug.start()
        elif stop:
            nodedebug.stop()
        else:
            nodedebug.start()
    except errors.KnownError as err:
        logger.fatal(err)


def run_tests(args):
    project = args.project
    wildcard = args.wildcard

    try:
        projects.run_tests(project, wildcard)
    except errors.KnownError as err:
        logger.fatal(err)


if __name__ == "__main__":
    main()
