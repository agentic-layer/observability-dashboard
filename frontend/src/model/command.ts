import {GraphState} from "@/model/graphstate.ts";

export class Command {
    type: string;
    execute: (graphState: GraphState) => void;

    constructor(type: string, execute: (graphState: GraphState) => void) {
        this.type = type;
        this.execute = execute;
    }
}
