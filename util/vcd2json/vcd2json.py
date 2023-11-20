"""Create WaveJSON text string from VCD file."""
import argparse
import json
import wavedrom
import sys


class _SignalDef:
    def __init__(self, name, sid, length):
        self._name = name
        self._sid = sid
        self._length = length
        self._wave = []
    def __str__(self):
        out = {
            "name" : self._name,
            "id" : self._sid,
            "legnth" : self._length,
            "wave" : self._wave
        }
        return json.dumps(out, indent=4)
    def add_signal(self, in_signal):
        self._wave.append(in_signal)


class WaveExtractor:

    def __init__(self, vcd_file, json_file):
        self._vcd_file = vcd_file
        self._json_file = json_file
        self._path_list = []
        self._icon_list = []
        self._path2signal = {}
        self._icon2signal = {}

    def parse_definition(self):
        def create_path_to_signal(fin):
            lines = fin.readlines()
            hier_list = []

            path_list = []
            path_dict = {}
            icon_list = []
            icon_dict = {}
            for line in lines:
                words = line.split()
                if words[0] == "$enddefinitions":
                    return path_list, path_dict, icon_list, icon_dict
                if words[0] == "$scope":
                    hier_list.append(words[2])
                elif words[0] == "$var":
                    path = "/".join(hier_list + [words[4]])
                    icon = words[3]
                    path_list.append(path)
                    icon_list.append(icon)
                    signal = _SignalDef(name=words[4], sid=words[3], length=int(words[2]))
                    path_dict[path] = signal
                    icon_dict[icon] = signal
                    # print(path)
                    # print(str(path_dict[path]))
                    # print(icon)
                    # print(str(icon_dict[icon]))
                elif words[0] == "$upscope":
                    del hier_list[-1]

        with open(self._vcd_file, "rt") as fin:
            self._path_list, self._path2signal,\
            self._icon_list, self._icon2signal \
                = create_path_to_signal(fin)
        
        # print(self._path_list)
        # print(self._path2signal)

    def parse_signal(self):
        with open(self._vcd_file, "rt") as fin:
            lines = fin.readlines()
            signal_added_check = set()
            for line in lines:
                words = line.split()
                if words[0] == "$dumpvars":
                    signal_added_check = set([icon for icon in self._icon_list])
                elif words[0][0] == "#":
                    for icon in signal_added_check:
                        self._icon2signal[icon].add_signal(self._icon2signal[icon]._wave[-1])
                    signal_added_check = set([icon for icon in self._icon_list])
                if words[0][0] == "b":
                    signal_added_check.remove(words[1])
                    self._icon2signal[words[1]].add_signal(words[0][1:])

    def dump_signal(self):
        json_signals = {"signal" : []}
        for path in self._path_list:
            json_signal = {}
            signal = self._path2signal[path]
            json_signal["name"] = path
            json_signal["wave"] = ""
            json_signal["data"] = []
            for w in signal._wave:
                if signal._length > 1:
                    json_signal["wave"] += "2"
                    if w != ".":
                        json_signal["data"].append(str(int(w,2)))
                    else:
                        json_signal["data"].append(w)
            json_signals["signal"].append(json_signal)
        
        with open(self._json_file, 'wt') as fout:
            fout.write(json.dumps(json_signals, indent=4))

        return json.dumps(json_signals, indent=4)


    def print_props(self):
        print("vcd_file  = '" + self._vcd_file + "'")
        print("json_file = '" + self._json_file + "'")

    def show_signals(self):
        print("Path list : ")
        print("    " + str(self._path_list))
        print("Icon list : ")
        print("    " + str(self._icon_list))
        print("Signal : ")
        for val in self._path2signal.values():
            print("    " + str(val))

# The argument parser
def Argument():
    parser = argparse.ArgumentParser(description="Mysql db manager")
    parser.add_argument('-f', '--file', type=str, required=True, help="specify the vcd file to convert to json")
    return parser.parse_args()

if __name__=="__main__":
    arg = Argument()
    prefix_name = arg.file.split(".")[0]
    extractor = WaveExtractor(prefix_name+".vcd", prefix_name+".json")
    extractor.parse_definition()
    extractor.parse_signal()
    # extractor.print_props()
    # extractor.show_signals()
    json_data = extractor.dump_signal()
    svg = wavedrom.render(json_data)
    svg.saveas(prefix_name+".svg")

