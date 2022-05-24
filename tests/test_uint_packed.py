import os

import pytest
from utils import assert_revert

CONTRACT_FILE = os.path.join("contracts", "uint_packed.cairo")

@pytest.fixture(scope="session")
async def contract(starknet):
    return await starknet.deploy(source=CONTRACT_FILE,)
  
@pytest.mark.asyncio
async def test_valid_felt(contract ):
    await contract.assert_valid_felt(0).invoke()
  
@pytest.mark.asyncio
async def test_valid_felt_limit(contract ):
    await contract.assert_valid_felt(127).invoke()
  
@pytest.mark.asyncio
async def test_join_to_outside(contract):
    await assert_revert(contract.assert_valid_felt(128).invoke(), "Error felt too big")
    
@pytest.mark.asyncio
async def assert_valid_felt_outside(contract):
    await assert_revert(contract.generate_get_mask(35).invoke(), "Error out of bound")

@pytest.mark.asyncio
@pytest.mark.parametrize("position, result",[
    (0,127),
    (1,16256),
    (5,4363686772736),
    (10,149935135831111235534848),
    (20,177012165013336821185939763789146369453719552),
    (30,208979078779793167353681086184783514132807454935464642645273346048),
    (34,56097394306713702464269695648587662877522613725800901920360996891040677888)
])
async def test_generate_get_mask(contract, position, result):
    execution_info = await contract.generate_get_mask(position).invoke()
    assert execution_info.result.mask == result


@pytest.mark.asyncio
@pytest.mark.parametrize("input, position, result",[
    (129,0,1),
    (128,0,0),
    (255,0,127),
    (56097394306713702464269695648587662877522613725800901920360996891040677888, 34, 127),
    (28711264802648745355728584387072425882196613324228808069476100771005071360, 34, 65)
])
async def test_view_get_element_at(contract, input, position, result):
    execution_info = await contract.view_get_element_at(input, position).invoke()
    assert execution_info.result.response == result


@pytest.mark.asyncio
@pytest.mark.parametrize("input, position, element, result",[
    (0,0,127,127),
    (0,1,127,16256),
    (0,5,127,4363686772736),
    (0,10,127,149935135831111235534848),
    (0,20,127,177012165013336821185939763789146369453719552),
    (0,30,127,208979078779793167353681086184783514132807454935464642645273346048),
    (0,34,127,56097394306713702464269695648587662877522613725800901920360996891040677888),
])
async def test_view_set_element_at(contract, input, position, element, result):
    execution_info = await contract.view_set_element_at(input, position, element).invoke()
    assert execution_info.result.response == result

@pytest.mark.asyncio
@pytest.mark.parametrize("input, position, element, result",[
    (4398046510976,0,127,4398046511103),
])
async def test_view_set_element_at_with_previous_value(contract, input, position, element, result):
    execution_info = await contract.view_set_element_at(input, position, element).invoke()
    assert execution_info.result.response == result
