# Evaluation report

- results: `..\mulita-extractor-training\output_heldout\mulita-qwen2.5-1.5b\nessus\20260809T212510Z_Nessus_VulnLab_scan-b_mulita-qwen2.5-1.5b\results.json`
- baseline: `C:\Users\Bia\Documents\GitHub\Projetos\mulita-extractor-training\data\heldout\nessus\Nessus_VulnLab_scan-b.xlsx`
- source: NESSUS — threshold 0.7 — text metrics: token_f1, rouge_l

## Coverage

- baseline findings: 268
- extracted records: 263
- matched: 257  (recall 0.959, precision 0.977)

## block_id drops

- 16 dropped (unknown_id=12, duplicate_id=3, validation_error=0, unrecovered=1)
  (unknown_id/duplicate_id: LLM output rejected; unrecovered: block yielded no record after retries)

## chunk retries

- 1 retried (bad_json=1, bad_shape=0)
  (bad_json: response not valid JSON, usually output truncated at the token cap; bad_shape: JSON parsed but failed the schema)

## Field scores (measured mean — vacuous empty×empty pairs excluded)

```
field             exact  set_f1  set_f1_ids  structural  rouge_l  token_f1
-----             -----  ------  ----------  ----------  -------  --------
name              -      -       -           -           0.999    0.999   
description       -      -       -           -           0.461    0.461   
solution          -      -       -           -           0.951    0.951   
impact            -      -       -           -           n/a      n/a     
references        -      0.844   0.844       -           -        -       
severity          0.977  -       -           -           -        -       
port              0.191  -       -           -           -        -       
protocol          0.191  -       -           -           -        -       
cvss              -      0.463   0.463       -           -        -       
insight           -      -       -           -           0.120    0.120   
detection_result  -      -       -           -           0.784    0.788   
plugin            0.984  -       -           -           -        -       
plugin_details    -      -       -           0.842       -        -       
```

`n/a` = every matched pair was empty on both sides for that field (nothing to measure). Inclusive means and per-pair detail live in `evaluation.json`.

## Worst pairs per field

- **name**: Apache CouchDB &lt; 3.2.3 / 3.3.x &lt; 3.3.2 Information Disclosure (0.929); Apache CouchDB &lt; 3.1.2 Privilege Escalation (0.933); Apache CouchDB &lt; 3.3.3 Privilege Escalation (0.933)
- **description**: IP Forwarding Enabled (0.0); ICMP Timestamp Request Remote Date Disclosure (0.0); Nessus SYN scanner (0.0); Nessus Scan Information (0.0); OS Fingerprints Detected (0.0)
- **solution**: ICMP Timestamp Request Remote Date Disclosure (0.0); Nessus SYN scanner (0.0); ICMP Timestamp Request Remote Date Disclosure (0.0); ICMP Timestamp Request Remote Date Disclosure (0.0); ICMP Timestamp Request Remote Date Disclosure (0.0)
- **references**: TCP/IP Timestamps Supported (0.0); Apache CouchDB Unauthenticated Administrative Access (0.0); Patch Report (0.0); Squid Proxy Version Detection (0.0); TCP/IP Timestamps Supported (0.0)
- **severity**: IP Forwarding Enabled (0.0); Traceroute Information (0.0); IP Forwarding Enabled (0.0); Apache Tomcat SEoL (6.0.x) (0.0); Additional DNS Hostnames (0.0)
- **port**: IP Forwarding Enabled (0.0); ICMP Timestamp Request Remote Date Disclosure (0.0); Common Platform Enumeration (CPE) (0.0); Device Type (0.0); Ethernet MAC Addresses (0.0)
- **protocol**: IP Forwarding Enabled (0.0); ICMP Timestamp Request Remote Date Disclosure (0.0); Common Platform Enumeration (CPE) (0.0); Device Type (0.0); Ethernet MAC Addresses (0.0)
- **cvss**: IP Forwarding Enabled (0.0); ICMP Timestamp Request Remote Date Disclosure (0.0); MongoDB Service Without Authentication Detection (0.0); IP Forwarding Enabled (0.0); Apache CouchDB &lt; 3.1.2 Privilege Escalation (0.0)
- **insight**: IP Forwarding Enabled (0.0); ICMP Timestamp Request Remote Date Disclosure (0.0); Common Platform Enumeration (CPE) (0.0); Device Type (0.0); Ethernet MAC Addresses (0.0)
- **detection_result**: TCP/IP Timestamps Supported (0.0); TCP/IP Timestamps Supported (0.0); Apache CouchDB &lt; 3.2.3 / 3.3.x &lt; 3.3.2 Information Disclosure (0.0); Apache CouchDB &lt; 3.3.3 Privilege Escalation (0.0); Squid Proxy Version Detection (0.0)
- **plugin**: Apache Tomcat SEoL (6.0.x) (0.0); Remote Services Not Using Post-Quantum Ciphers (0.0); SSL / TLS Versions Supported (0.0); SSL Certificate Information (0.0)
- **plugin_details**: Apache Tomcat SEoL (6.0.x) (0.0); Apache CouchDB &lt; 3.1.2 Privilege Escalation (0.3); Apache CouchDB Unauthenticated Administrative Access (0.3); Traceroute Information (0.3); IP Forwarding Enabled (0.3)

## False negatives (in baseline, not extracted)

- Apache Tomcat AJP Connector Request Injection (Ghostcat)
- Service Detection
- SSL Self-Signed Certificate
- HSTS Missing From HTTPS Server
- SSL Certificate Information
- SSL Cipher Suites Supported
- SSL Cipher Suites Supported
- TLS Version 1.3 Protocol Detection
- SSL Cipher Block Chaining Cipher Suites Supported
- SSL Cipher Suites Supported
- SSL Perfect Forward Secrecy Cipher Suites Supported

## False positives (extracted, not in baseline)

- SSL Version Information
- tcp/9090/www
- tcp/8080/www
- tcp/10000/www
- tcp/10000/www
- tcp/10000/www

## Notes

- baseline never fills `impact` — scores there only measure presence agreement: 1.0 means the extraction also left the field empty; low values mean it filled a field the ground truth does not annotate.
