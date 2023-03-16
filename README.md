
# Groovy API Tests

This repository contains REST API Testing automation code using Python for a Groovy execution service.

The project uses:
1. Python 3.9 and higher
2. Pytest
3. Requests
4. Allure Framework for reports
5. CI (GitHub actions)

## Test Arguments

The following default arguments are common to multiple tests:
* `--testbed=resources/testbeds/local_host.yml` defines the environment being tested
* `--validationConfig=resources/validation/validation_config.yml` defines validation used by some tests

### How to run tests

- **Without Allure Test report**
```
python -m pytest -v  test/test_groovy_api.py
```
- **With Allure Test report**
```
 python -m pytest -v  --alluredir=target/allure_reports  test/test_groovy_api.py  
```
Show generated report in browser:
```
 allure serve target/allure_reports 
```