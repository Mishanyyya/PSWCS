#!/usr/bin/env sh

set -eu

# Конфигурация
SERVICES_DIR="services"
SERVICES="users review university"
MIN_COVERAGE=70

# Функция для запуска тестов в сервисе
run_tests_for_service() {
    local service=$1
    local service_dir="$SERVICES_DIR/$service"
    
    echo ""
    echo "========================================="
    echo "Running tests for $service service"
    echo "========================================="
    
    # Проверяем существование директории
    if [ ! -d "$service_dir" ]; then
        printf "WARNING: Service directory %s not found, skipping...\n" "$service_dir"
        return 0
    fi
    
    # Активируем виртуальное окружение если есть
    if [ -f "$service_dir/.venv/bin/activate" ]; then
        # shellcheck disable=SC1091
        . "$service_dir/.venv/bin/activate"
    fi
    
    # Проверяем установлен ли pytest
    command -v pytest >/dev/null 2>&1 || {
        printf "ERROR: pytest not installed for %s\n" "$service"
        return 1
    }
    
    # Проверяем установлен ли pytest-cov
    python -c "import pytest_cov" >/dev/null 2>&1 || {
        printf "ERROR: pytest-cov not installed for %s\n" "$service"
        return 1
    }
    
    # Запускаем тесты
    (
        cd "$service_dir"
        
        # Определяем путь к тестам (может быть tests/ или app/tests/)
        if [ -d "tests" ]; then
            tests_path="tests/"
        elif [ -d "app/tests" ]; then
            tests_path="app/tests/"
        else
            printf "WARNING: No tests directory found in %s\n" "$service"
            return 0
        fi
        
        # Запускаем pytest с покрытием
        pytest $tests_path \
            --cov=app \
            --cov-report=term-missing \
            --cov-report=html \
            --cov-fail-under="$MIN_COVERAGE" \
            -q --tb=short
        
        local exit_code=$?
        if [ $exit_code -ne 0 ]; then
            printf "ERROR: Tests failed for %s service\n" "$service"
            return $exit_code
        fi
    )
    
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        printf "OK %s coverage >= %s%%\n" "$service" "$MIN_COVERAGE"
    fi
    
    return $exit_code
}

# Основная логика
main() {
    local failed=0
    
    printf "Starting tests for all services...\n"
    printf "Services to test: %s\n" "$SERVICES"
    
    # Проверяем существование директории services
    if [ ! -d "$SERVICES_DIR" ]; then
        printf "ERROR: Services directory '%s' not found\n" "$SERVICES_DIR"
        exit 1
    fi
    
    # Запускаем тесты для каждого сервиса
    for service in $SERVICES; do
        if ! run_tests_for_service "$service"; then
            failed=1
        fi
    done
    
    # Выводим итоговый результат
    echo ""
    echo "========================================="
    if [ $failed -eq 0 ]; then
        printf "SUCCESS: All services passed tests with coverage >= %s%%\n" "$MIN_COVERAGE"
        exit 0
    else
        printf "FAILED: Some services failed tests\n"
        exit 1
    fi
}

# Запускаем основную функцию
main