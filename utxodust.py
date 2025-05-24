import csv

p2pkh_total = 0
p2pkh_dust = 0
p2wpkh_total = 0
p2wpkh_dust = 0
p2wsh_total = 0
p2wsh_dust = 0
p2tr_total = 0
p2tr_dust = 0
other_total = 0
other_dust = 0

with open('utxoset.csv', newline='') as f:
    # discard header line
    next(f)

    reader = csv.DictReader(f)
    reader.fieldnames = ['value', 'scriptPubKey']

    for row in reader:
        value = int(row['value'])
        spk = row['scriptPubKey']

        if spk.startswith('76a914') and spk.endswith('88ac') and len(spk) == 50:
            p2pkh_total += 1
            if value < 1000:
                p2pkh_dust += 1
            continue

        if spk.startswith('0014') and len(spk) == 44:
            p2wpkh_total += 1
            if value < 1000:
                p2wpkh_dust += 1
            continue

        if spk.startswith('0020') and len(spk) == 68:
            p2wsh_total += 1
            if value < 1000:
                p2wsh_dust += 1
            continue

        if spk.startswith('5120') and len(spk) == 68:
            p2tr_total += 1
            if value < 1000:
                p2tr_dust += 1
            continue

        other_total += 1
        if value < 1000:
            other_dust += 1

def print_summary(name: str, total: int, dust: int) -> None:
    pct = (dust / total * 100) if total > 0 else 0
    print(f"total {name} outputs: {total}")
    print(f" dust {name} outputs: {dust} ({pct:.2f}%)\n")

print_summary("P2PKH", p2pkh_total, p2pkh_dust)
print_summary("P2WPKH", p2wpkh_total, p2wpkh_dust)
print_summary("P2WSH", p2wsh_total, p2wsh_dust)
print_summary("P2TR", p2tr_total, p2tr_dust)
print_summary("other", other_total, other_dust)
