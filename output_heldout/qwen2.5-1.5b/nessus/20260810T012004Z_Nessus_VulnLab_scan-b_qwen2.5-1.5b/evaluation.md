# Evaluation report

- results: `..\mulita-extractor-training\output_heldout\qwen2.5-1.5b\nessus\20260810T012004Z_Nessus_VulnLab_scan-b_qwen2.5-1.5b\results.json`
- baseline: `C:\Users\Bia\Documents\GitHub\Projetos\mulita-extractor-training\data\heldout\nessus\Nessus_VulnLab_scan-b.xlsx`
- source: NESSUS — threshold 0.7 — text metrics: token_f1, rouge_l

## Coverage

- baseline findings: 268
- extracted records: 246
- matched: 243  (recall 0.907, precision 0.988)

## block_id drops

- 1 dropped (unknown_id=0, duplicate_id=0, validation_error=0, unrecovered=1)
  (unknown_id/duplicate_id: LLM output rejected; unrecovered: block yielded no record after retries)

## chunk retries

- 4 retried (bad_json=4, bad_shape=0)
  (bad_json: response not valid JSON, usually output truncated at the token cap; bad_shape: JSON parsed but failed the schema)

## Field scores (measured mean — vacuous empty×empty pairs excluded)

```
field             exact  set_f1  set_f1_ids  structural  rouge_l  token_f1
-----             -----  ------  ----------  ----------  -------  --------
name              -      -       -           -           0.998    0.998   
description       -      -       -           -           0.001    0.001   
solution          -      -       -           -           0.004    0.004   
impact            -      -       -           -           n/a      n/a     
references        -      0.009   0.009       -           -        -       
severity          0.963  -       -           -           -        -       
port              0.000  -       -           -           -        -       
protocol          0.000  -       -           -           -        -       
cvss              -      0.224   0.224       -           -        -       
insight           -      -       -           -           0.000    0.000   
detection_result  -      -       -           -           0.000    0.000   
plugin            0.963  -       -           -           -        -       
plugin_details    -      -       -           0.856       -        -       
```

`n/a` = every matched pair was empty on both sides for that field (nothing to measure). Inclusive means and per-pair detail live in `evaluation.json`.

## Worst pairs per field

- **name**: Apache Tomcat SEoL (6.0.x) (0.667); Apache CouchDB &lt; 3.2.3 / 3.3.x &lt; 3.3.2 Information Disclosure (0.929); Apache CouchDB &lt; 3.1.2 Privilege Escalation (0.933); Apache CouchDB &lt; 3.3.3 Privilege Escalation (0.933)
- **description**: IP Forwarding Enabled (0.0); ICMP Timestamp Request Remote Date Disclosure (0.0); Common Platform Enumeration (CPE) (0.0); Device Type (0.0); Ethernet MAC Addresses (0.0)
- **solution**: IP Forwarding Enabled (0.0); ICMP Timestamp Request Remote Date Disclosure (0.0); Common Platform Enumeration (CPE) (0.0); Device Type (0.0); Ethernet MAC Addresses (0.0)
- **references**: IP Forwarding Enabled (0.0); ICMP Timestamp Request Remote Date Disclosure (0.0); Common Platform Enumeration (CPE) (0.0); PostgreSQL Server Detection (0.0); TCP/IP Timestamps Supported (0.0)
- **severity**: Traceroute Information (0.0); Patch Report (0.0); Traceroute Information (0.0); Traceroute Information (0.0); Traceroute Information (0.0)
- **port**: IP Forwarding Enabled (0.0); ICMP Timestamp Request Remote Date Disclosure (0.0); Common Platform Enumeration (CPE) (0.0); Device Type (0.0); Ethernet MAC Addresses (0.0)
- **protocol**: IP Forwarding Enabled (0.0); ICMP Timestamp Request Remote Date Disclosure (0.0); Common Platform Enumeration (CPE) (0.0); Device Type (0.0); Ethernet MAC Addresses (0.0)
- **cvss**: IP Forwarding Enabled (0.0); ICMP Timestamp Request Remote Date Disclosure (0.0); MongoDB Service Without Authentication Detection (0.0); IP Forwarding Enabled (0.0); ICMP Timestamp Request Remote Date Disclosure (0.0)
- **insight**: IP Forwarding Enabled (0.0); ICMP Timestamp Request Remote Date Disclosure (0.0); Common Platform Enumeration (CPE) (0.0); Device Type (0.0); Ethernet MAC Addresses (0.0)
- **detection_result**: IP Forwarding Enabled (0.0); ICMP Timestamp Request Remote Date Disclosure (0.0); Common Platform Enumeration (CPE) (0.0); Device Type (0.0); Ethernet MAC Addresses (0.0)
- **plugin**: ICMP Timestamp Request Remote Date Disclosure (0.0); Apache CouchDB &lt; 3.2.3 / 3.3.x &lt; 3.3.2 Information Disclosure (0.0); AMQP Cleartext Authentication (0.0); IP Forwarding Enabled (0.0); ICMP Timestamp Request Remote Date Disclosure (0.0)
- **plugin_details**: Apache Tomcat SEoL (6.0.x) (0.0); SSL Certificate Information (0.0); SSL Cipher Block Chaining Cipher Suites Supported (0.0); OS Fingerprints Detected (0.8); IP Forwarding Enabled (0.867)

## False negatives (in baseline, not extracted)

- Nessus SYN scanner
- Apache Tomcat AJP Connector Request Injection (Ghostcat)
- Nessus SYN scanner
- HTTP Server Type and Version
- Nessus SYN scanner
- Service Detection
- SSL Certificate Cannot Be Trusted
- HSTS Missing From HTTPS Server
- HyperText Transfer Protocol (HTTP) Information
- Nessus SYN scanner
- Remote Services Using Post-Quantum Ciphers
- SSL / TLS Versions Supported
- SSL Certificate Information
- SSL Cipher Suites Supported
- SSL Perfect Forward Secrecy Cipher Suites Supported
- SSL/TLS Recommended Cipher Suites
- Service Detection
- TLS Supported Groups
- TLS Version 1.2 Protocol Detection
- TLS Version 1.3 Protocol Detection
- DNS Server Detection
- Nessus SYN scanner
- SSL Cipher Block Chaining Cipher Suites Supported
- SSL Cipher Suites Supported
- SSL Perfect Forward Secrecy Cipher Suites Supported

## False positives (extracted, not in baseline)

- tcp/10000/www
- tcp/10000/www
- tcp/10000/www

## Notes

- baseline never fills `impact` — scores there only measure presence agreement: 1.0 means the extraction also left the field empty; low values mean it filled a field the ground truth does not annotate.
