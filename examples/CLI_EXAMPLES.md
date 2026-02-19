# Ditto CLI - Device Examples Guide

This guide demonstrates working with devices of varying complexity using the Eclipse Ditto CLI. We'll create, list, and interact with 5 different devices ranging from simple sensors to complex smart devices.

## Prerequisites

Ensure your environment variables are set:

```bash
export DITTO_BASE_URL="http://host.docker.internal:8080"
export DITTO_USERNAME="ditto"
export DITTO_PASSWORD="ditto"
export DITTO_DEVOPS_USERNAME="devops"
export DITTO_DEVOPS_PASSWORD="foobar"
```

## Setup: Create the Policy

First, create the policy that will be used by all devices:

```bash
uv run ditto-client policy create "my.sensors:sample-policy" examples/cli-examples/policy.json
```

Verify the policy was created:

```bash
uv run ditto-client policy get "my.sensors:sample-policy"
```

---

## Device 1: Simple Temperature Sensor

A minimal device with one feature and basic attributes.

### Create the Device

```bash
uv run ditto-client thing create "my.sensors:temp-sensor" examples/cli-examples/thing-temperature.json
```

### View the Device

```bash
uv run ditto-client thing get "my.sensors:temp-sensor"
```

---

## Device 2: Humidity Sensor

A sensor with multiple properties and timestamps.

### Create the Device

```bash
uv run ditto-client thing create "my.sensors:humidity-sensor" examples/cli-examples/thing-humidity.json
```

### View the Device

```bash
uv run ditto-client thing get "my.sensors:humidity-sensor"
```

---

## Device 3: Smart Thermostat

A complex HVAC controller with multiple features, scheduling, and diagnostics.

### Create the Device

```bash
uv run ditto-client thing create "my.home:thermostat-bedroom" examples/cli-examples/thing-thermostat.json
```

### View the Complete Device

```bash
uv run ditto-client thing get "my.home:thermostat-bedroom"
```

---

## Device 4: Door Camera

A sophisticated device with multiple subsystems, network configuration, and advanced features.

### Create the Device

```bash
uv run ditto-client thing create "my.security:door-camera" examples/cli-examples/thing-door-camera.json
```

### View the Complete Device

```bash
uv run ditto-client thing get "my.security:door-camera"
```

---

## Device 5: Kitchen Camera

A sophisticated device with multiple subsystems, network configuration, and advanced features.

### Create the Device

```bash
uv run ditto-client thing create "my.security:kitchen-camera" examples/cli-examples/thing-kitchen-camera.json
```

### View the Complete Device

```bash
uv run ditto-client thing get "my.security:kitchen-camera"
```

---

## List

### List All Devices

```bash
uv run ditto-client thing list
```

### List with Table View

```bash
uv run ditto-client --table thing list
```

### List Specific Devices by ID

```bash
uv run ditto-client thing list --ids "my.sensors:temp-sensor,my.sensors:humidity-sensor,my.home:thermostat-bedroom"
```

### List with Selected Fields

```bash
uv run ditto-client thing list --fields "thingId,attributes/location,attributes/manufacturer"
```

---

## Search

### Search by Location (Kitchen)

```bash
uv run ditto-client search query --filter 'eq(attributes/location,"Kitchen")'
```

### Search by Namespace

```bash
uv run ditto-client search query --namespaces "my.sensors"
```

### Search for Devices with Temperature Feature

```bash
uv run ditto-client search query --filter 'exists(features/temperature)'
```

### Search for Smart Home Devices in Bedroom

```bash
uv run ditto-client search query --filter 'like(attributes/location,"*Bedroom*")'
```
---

### Count All Devices

```bash
uv run ditto-client search count
```

### Count Devices in Specific Namespace

```bash
uv run ditto-client search count --namespaces "my.sensors"
```

---

## Cleanup

Delete all test devices:

```bash
uv run ditto-client thing delete "my.sensors:temp-sensor"
uv run ditto-client thing delete "my.sensors:humidity-sensor"
uv run ditto-client thing delete "my.home:thermostat-bedroom"
uv run ditto-client thing delete "my.security:door-camera"
uv run ditto-client thing delete "my.security:kitchen-camera"
```

Delete the policy:

```bash
uv run ditto-client policy delete "my.sensors:sensor-policy"
```
