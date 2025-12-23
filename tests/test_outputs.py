"""Tests for Yarn v3 workspace peer dependency resolution task."""
import json
import subprocess
import hashlib
from pathlib import Path


def test_package_json_files_exist():
    """Verify all required package.json files exist in the workspace."""
    root_pkg = Path("/app/package.json")
    ui_lib_pkg = Path("/app/packages/ui-lib/package.json")
    dashboard_pkg = Path("/app/packages/dashboard/package.json")
    analytics_pkg = Path("/app/packages/analytics/package.json")
    
    assert root_pkg.exists(), "Root package.json does not exist"
    assert ui_lib_pkg.exists(), "ui-lib package.json does not exist"
    assert dashboard_pkg.exists(), "dashboard package.json does not exist"
    assert analytics_pkg.exists(), "analytics package.json does not exist"


def test_yarn_lock_exists():
    """Verify yarn.lock file was generated."""
    yarn_lock = Path("/app/yarn.lock")
    assert yarn_lock.exists(), "yarn.lock file does not exist"
    
    content = yarn_lock.read_text()
    assert len(content) > 100, "yarn.lock file appears to be empty or incomplete"


def test_install_state_exists():
    """Verify .yarn/install-state.gz file was generated."""
    install_state = Path("/app/.yarn/install-state.gz")
    assert install_state.exists(), ".yarn/install-state.gz does not exist"


def test_corepack_enabled():
    """Verify Corepack is enabled and Yarn v3 is available."""
    result = subprocess.run(
        ["yarn", "--version"],
        capture_output=True,
        text=True,
        cwd="/app"
    )
    
    assert result.returncode == 0, "yarn command failed"
    version = result.stdout.strip()
    assert version.startswith("3."), f"Expected Yarn v3.x but got {version}"


def test_peer_dependencies_aligned():
    """Verify all workspace packages have aligned React peer dependencies."""
    ui_lib_pkg = json.loads(Path("/app/packages/ui-lib/package.json").read_text())
    dashboard_pkg = json.loads(Path("/app/packages/dashboard/package.json").read_text())
    analytics_pkg = json.loads(Path("/app/packages/analytics/package.json").read_text())
    
    # Check that all packages have compatible React dependencies
    ui_lib_react = ui_lib_pkg.get("dependencies", {}).get("react", "")
    dashboard_react = dashboard_pkg.get("dependencies", {}).get("react", "")
    analytics_react = analytics_pkg.get("dependencies", {}).get("react", "")
    
    # All should be React 18.x
    assert "18" in ui_lib_react, f"ui-lib React version {ui_lib_react} should be 18.x"
    assert "18" in dashboard_react, f"dashboard React version {dashboard_react} should be 18.x"
    assert "18" in analytics_react, f"analytics React version {analytics_react} should be 18.x"
    
    # Check peer dependencies are also aligned
    ui_lib_peer = ui_lib_pkg.get("peerDependencies", {}).get("react", "")
    dashboard_peer = dashboard_pkg.get("peerDependencies", {}).get("react", "")
    analytics_peer = analytics_pkg.get("peerDependencies", {}).get("react", "")
    
    assert "18" in ui_lib_peer, "ui-lib peer dependency should be React 18.x"
    assert "18" in dashboard_peer, "dashboard peer dependency should be React 18.x"
    assert "18" in analytics_peer, "analytics peer dependency should be React 18.x"


def test_workspaces_structure_maintained():
    """Verify the workspaces structure is maintained in root package.json."""
    root_pkg = json.loads(Path("/app/package.json").read_text())
    
    assert "workspaces" in root_pkg, "workspaces field is missing from root package.json"
    workspaces = root_pkg["workspaces"]
    
    assert "packages/*" in workspaces, "packages/* workspace pattern is missing"


def test_yarn_install_immutable_succeeds():
    """Verify yarn install --immutable runs successfully without errors."""
    result = subprocess.run(
        ["yarn", "install", "--immutable"],
        capture_output=True,
        text=True,
        cwd="/app"
    )
    
    assert result.returncode == 0, (
        f"yarn install --immutable failed with exit code {result.returncode}\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    
    # Check for error keywords in output
    combined_output = result.stdout + result.stderr
    assert "YN0000" in combined_output or result.returncode == 0, "yarn install did not complete successfully"


def test_no_peer_dependency_warnings():
    """Verify there are no peer dependency conflict warnings in yarn output."""
    result = subprocess.run(
        ["yarn", "install", "--immutable"],
        capture_output=True,
        text=True,
        cwd="/app"
    )
    
    combined_output = result.stdout + result.stderr
    
    # Check for common Yarn warning codes related to peer dependencies
    assert "YN0060" not in combined_output, "Found unmet peer dependency warning (YN0060)"
    assert "YN0002" not in combined_output, "Found missing peer dependency warning (YN0002)"
    assert "peer dependency" not in combined_output.lower() or "warning" not in combined_output.lower(), (
        "Found peer dependency warnings in output"
    )


def test_node_modules_populated():
    """Verify node_modules were created and contain React packages."""
    node_modules = Path("/app/node_modules")
    assert node_modules.exists(), "node_modules directory does not exist"
    
    # Check that React was installed
    react_dir = Path("/app/node_modules/react")
    assert react_dir.exists(), "React package not found in node_modules"
    
    # Verify React version is 18.x
    react_pkg = json.loads((react_dir / "package.json").read_text())
    react_version = react_pkg.get("version", "")
    assert react_version.startswith("18."), f"Expected React 18.x but got {react_version}"


def test_single_react_version_installed():
    """Verify only one version of React is installed in the workspace."""
    result = subprocess.run(
        ["yarn", "why", "react"],
        capture_output=True,
        text=True,
        cwd="/app"
    )
    
    # Count how many different React versions are mentioned
    lines = result.stdout.split("\n")
    react_versions = set()
    
    for line in lines:
        if "react@npm:" in line and "@" in line:
            # Extract version from lines like "react@npm:18.2.0"
            parts = line.split("@npm:")
            if len(parts) > 1:
                version = parts[1].split()[0]
                react_versions.add(version)
    
    assert len(react_versions) <= 1, (
        f"Multiple React versions found: {react_versions}. Should have only one version."
    )


def test_reproducibility_yarn_lock():
    """Verify yarn.lock remains unchanged after a second clean install."""
    # Save original lock file hash
    yarn_lock_path = Path("/app/yarn.lock")
    original_content = yarn_lock_path.read_text()
    original_hash = hashlib.sha256(original_content.encode()).hexdigest()
    
    # Clean install
    subprocess.run(["rm", "-rf", "/app/node_modules"], check=True)
    subprocess.run(["rm", "-rf", "/app/packages/ui-lib/node_modules"], check=True)
    subprocess.run(["rm", "-rf", "/app/packages/dashboard/node_modules"], check=True)
    subprocess.run(["rm", "-rf", "/app/packages/analytics/node_modules"], check=True)
    subprocess.run(["rm", "-rf", "/app/.yarn/cache"], check=True)
    subprocess.run(["rm", "-f", "/app/.yarn/install-state.gz"], check=True)
    
    # Reinstall
    result = subprocess.run(
        ["yarn", "install", "--immutable"],
        capture_output=True,
        text=True,
        cwd="/app"
    )
    
    assert result.returncode == 0, "Second install failed"
    
    # Verify lock file unchanged
    new_content = yarn_lock_path.read_text()
    new_hash = hashlib.sha256(new_content.encode()).hexdigest()
    
    assert original_hash == new_hash, (
        "yarn.lock changed after second install - not reproducible"
    )


def test_reproducibility_install_state():
    """Verify install-state.gz is identical after consecutive clean installs."""
    # First install state
    install_state_path = Path("/app/.yarn/install-state.gz")
    first_content = install_state_path.read_bytes()
    first_hash = hashlib.sha256(first_content).hexdigest()
    
    # Clean and reinstall
    subprocess.run(["rm", "-rf", "/app/node_modules"], check=True)
    subprocess.run(["rm", "-rf", "/app/packages/*/node_modules"], shell=True, check=True)
    subprocess.run(["rm", "-rf", "/app/.yarn/cache"], check=True)
    subprocess.run(["rm", "-f", "/app/.yarn/install-state.gz"], check=True)
    
    result = subprocess.run(
        ["yarn", "install", "--immutable"],
        capture_output=True,
        text=True,
        cwd="/app"
    )
    
    assert result.returncode == 0, "Reinstall failed"
    
    # Second install state
    second_content = install_state_path.read_bytes()
    second_hash = hashlib.sha256(second_content).hexdigest()
    
    assert first_hash == second_hash, (
        "install-state.gz changed after reinstall - not reproducible"
    )


def test_workspace_packages_accessible():
    """Verify workspace packages can reference each other correctly."""
    # Check that ui-lib is accessible from node_modules
    ui_lib_link = Path("/app/node_modules/@monorepo/ui-lib")
    dashboard_link = Path("/app/node_modules/@monorepo/dashboard")
    analytics_link = Path("/app/node_modules/@monorepo/analytics")
    
    assert ui_lib_link.exists(), "ui-lib not accessible via node_modules"
    assert dashboard_link.exists(), "dashboard not accessible via node_modules"
    assert analytics_link.exists(), "analytics not accessible via node_modules"
