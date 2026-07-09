# Sunbeam Cheat Sheet — Known Issues & Workarounds

Searchable log of real Sunbeam / Canonical OpenStack problems and fixes.
Search by error string, failing step, or component.

## Entry template (copy this when adding a new entry)

```
## <Title — short searchable symptom>

- **Component / Step:** <e.g. k8s / Terraform apply, MAAS mode, Juju, Neutron>
- **Symptom:** <exact error message(s), copied verbatim, + observable behavior>
- **Root cause:** <why it happens>
- **Workaround:**
  <exact commands / manifest snippet>
- **Notes:** <gotchas, bug link, date, confirmed-by>
```

---

## Index

| # | Title | Component / Step |
|---|-------|------------------|
| 1 | Cilium crashloop: "unable to determine direct routing device" (all-bridge network layout) | k8s / Terraform apply (MAAS mode) |

---

## 1. Cilium crashloop: "unable to determine direct routing device" (all-bridge network layout)

- **Component / Step:** `k8s` charm / K8S Terraform plan (MAAS mode). Blocks
  MetalLB → Sunbeam reports `Feature 'load-balancer' is not ready`.

- **Symptom:** During the K8S step, Cilium agent pods crashloop:

  ```
  sudo k8s kubectl get pods -n kube-system
  NAME              READY   STATUS             RESTARTS
  cilium-86v78      0/1     CrashLoopBackOff   5
  cilium-wqbzh      0/1     CrashLoopBackOff   5
  cilium-f4m8c      0/1     Running            6
  ...
  coredns-*         0/1     Pending
  metrics-server-*  0/1     Pending
  ```

  Cilium logs:

  ```
  level=error msg="Failed to start hive" error="daemon creation failed: unable to determine direct routing device. Use --direct-routing-device to specify it"
  ```

  Deployment eventually fails with:

  ```
  message="Feature 'load-balancer' is not ready"
  ```

  Network layout that triggers it: all node/VLAN interfaces terminate on **OVS
  bridges** (e.g. VLANs `3404/3405/3407/3408` on one OVS bridge, `3403/3406/3409`
  on another → `br-bond2`). Every candidate interface Cilium sees is a bridge.

- **Root cause:** Cilium auto-detects a "direct routing device" for native
  routing but **deliberately excludes bridge-type devices** from auto-detection.
  When *every* candidate interface is a bridge, no candidates remain →
  detection fails → agent crashloops → CNI never ready → coredns/metrics-server
  stay Pending → MetalLB can't come up → `load-balancer` feature check fails.
  It is NOT an unsupported topology; auto-detection just has nothing to pick.

- **Workaround:** Pin the Cilium device explicitly via the `k8s` charm
  `cluster-annotations`, pointing at the **internal** VLAN interface (bridge is
  fine when named explicitly). Use the internal space device (`br-bond2.3403`),
  not a storage/provider VLAN. Value must be identical on all nodes.

  Preferred (declarative, via Sunbeam manifest — reproducible on redeploy):

  ```yaml
  software:
    charms:
      k8s:
        channel: 1.32/stable
        config:
          cluster-annotations: "k8sd/v1alpha1/cilium/devices=br-bond2.3403"
  ```

  Live unblock (imperative):

  ```bash
  juju config k8s cluster-annotations="k8sd/v1alpha1/cilium/devices=br-bond2.3403"
  ```

- **Notes:**
  - Pick the interface for the **internal** Juju space (VLAN 3403 in the lab
    layout). Wrong VLAN (provider 3409 / storage) will "start" Cilium but route
    pod traffic over the wrong fabric.
  - Cluster-wide annotation → the named interface must exist on every worker/
    control node with the same name.
  - Real bug to file against Canonical K8s (k8sd): all-bridge topologies should
    either auto-select the device or fail with a clear, actionable message
    instead of a Cilium crashloop. Workaround required until then.
  - Confirmed: 2026-07 (MAAS-mode deploy, snap-openstack).
