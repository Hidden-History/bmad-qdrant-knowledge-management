#!/bin/bash
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "PHASE 5: COMPREHENSIVE VALIDATION TEST SUITE"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

total_tests=0
total_passed=0

run_test() {
    local test_file=$1
    local test_name=$2
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Running: $test_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    output=$(python3 "$test_file" 2>&1)
    exit_code=$?

    # Extract test counts from output
    passed=$(echo "$output" | grep "Tests Passed:" | grep -o '[0-9]\+' | head -1)
    run=$(echo "$output" | grep "Total Tests:" | grep -o '[0-9]\+' | head -1)

    if [ $exit_code -eq 0 ]; then
        echo "✅ $test_name: $passed/$run tests passed"
        total_tests=$((total_tests + run))
        total_passed=$((total_passed + passed))
    else
        echo "❌ $test_name: FAILED (exit code: $exit_code)"
    fi
    echo ""
}

run_test "test_all_schemas.py" "Schema Validation"
run_test "test_duplicate_detection.py" "Duplicate Detection"
run_test "test_storage_workflow.py" "Storage Workflow"
run_test "test_inventory_updates.py" "Inventory Updates"
run_test "test_monthly_review.py" "Monthly Review"
run_test "test_security_hardening.py" "Security Hardening"

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "FINAL RESULTS"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "Total Tests: $total_tests"
echo "Tests Passed: $total_passed"
echo "Tests Failed: $((total_tests - total_passed))"
echo "Success Rate: $(awk "BEGIN {printf \"%.1f\", ($total_passed/$total_tests)*100}")%"
echo ""

if [ $total_passed -eq $total_tests ]; then
    echo "✅ ALL PHASE 5 VALIDATION TESTS PASSED"
    echo "🚀 READY FOR PRODUCTION DEPLOYMENT"
    exit 0
else
    echo "⚠️  SOME TESTS FAILED - REVIEW ABOVE"
    exit 1
fi
