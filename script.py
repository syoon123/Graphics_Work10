import mdl
from display import *
from matrix import *
from draw import *
import pprint

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)
  
  Should set num_frames and basename if the frames 
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.

  jdyrlandweaver
  ==================== """
def first_pass( commands ):
    num_frames = 0
    frames_cmd = False
    basename = "frame"
    basename_cmd = False
    vary_cmd = False

    for command in commands:
        if command[0] == "frames":
            num_frames = int(command[1])
            frames_cmd = True
        if command[0] == "basename":
            basename = command[1]
            basename_cmd = True
        if command[0] == "vary":
            vary_cmd = True

    if vary_cmd:
        if not frames_cmd:
            print "Error -- frames command not found."
            exit()
    if frames_cmd:
        if not basename_cmd:
            print "Using default basename, \"" + basename + "\""

    return (num_frames, basename)        


"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go 
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value. 
  ===================="""
def second_pass( commands, num_frames ):
    knobs = [ {} for frame in range(num_frames + 1) ]
    for command in commands:
        if command[0] == "vary":
            start_frame = command[2]
            end_frame = command[3]
            frame_diff = (end_frame - start_frame)
            knob_scale = command[5] - command[4]
            start_knob_val = float(knob_scale) / frame_diff
            for frame in range(start_frame, end_frame + 1):
                value = start_knob_val * (frame - start_frame)
                knobs[frame][command[1]] = command[4] + value
    return knobs


def run(filename):
    """
    This function runs an mdl script
    """
    color = [255, 255, 255]
    tmp = new_matrix()
    ident( tmp )

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    (num_frames, basename) = first_pass(commands)
    knob_values = second_pass(commands, num_frames)
    ident(tmp)
    stack = [ [x[:] for x in tmp] ]
    screen = new_screen()
    tmp = []
    step = 0.1
    for frame in range(num_frames):
        knobs = knob_values[frame]

        for command in commands:
            c = command[0]
            args = command[1:]

            if c == 'box':
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'torus':
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'set':
                if args[0] in knobs:
                    knobs[args[0]] = float(args[1])
            elif c == 'set_knobs':
                for knob in knobs.keys():
                    knobs[knob] = args[0]        
            elif c == 'move':
                if args[-1] != None and args[-1] in knobs:
                    args = [arg * knobs[args[-1]] for arg in args[:3]]
                tmp = make_translate(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                if args[-1] != None and args[-1] in knobs:
                    args = [arg * knobs[args[-1]] for arg in args[:3]]
                tmp = make_scale(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180)
                if args[-1] != None and args[-1] in knobs:
                    theta *= knobs[args[-1]]
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                    matrix_mult( stack[-1], tmp )
                    stack[-1] = [ x[:] for x in tmp]
                    tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
                
        if num_frames > 1:
            print "Saved frame in anim. Filename: " + basename + str(frame) + ".png"
            save_extension(screen, "anim/" + basename + str(frame) + ".png")

        clear_screen(screen)
        tmp = new_matrix()
        ident(tmp)
        stack = [ [x[:] for x in tmp] ]
        tmp = []

    if num_frames > 1:
        make_animation(basename)
    
